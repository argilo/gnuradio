#!/usr/bin/env python
#
# Copyright 2014 Free Software Foundation, Inc.
# Copyright 2023 Daniel Estevez <daniel@destevez.net>
#
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#

# This is similar to _qa_helper.py but uses async_encoder and async_decoder
# instead of extended_encoder and extended_decoder.


import numpy as np

from gnuradio import gr, blocks, fec
# Must use absolute import here because this file is not installed as part
# of the module
from gnuradio.fec import async_encoder, async_decoder
import pmt
import queue


class _pdu_sender(gr.sync_block):
    def __init__(self, frame_size):
        gr.sync_block.__init__(
            self,
            name="_pdu_sender",
            in_sig=[np.uint8],
            out_sig=None
        )
        self.frame_size = frame_size
        self.set_output_multiple(self.frame_size)
        self.message_port_register_out(pmt.intern('pdus'))

    def work(self, input_items, output_items):
        in0 = input_items[0]
        for offset in range(0, len(in0), self.frame_size):
            values = in0[offset:offset+self.frame_size]
            pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(self.frame_size, values))
            self.message_port_pub(pmt.intern('pdus'), pdu)
        return len(in0)


class _pdu_converter(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(
            self,
            name="_pdu_converter",
            in_sig=None,
            out_sig=None
        )
        self.message_port_register_in(pmt.intern('pdus_in'))
        self.set_msg_handler(pmt.intern('pdus_in'),
                             self.handle_msg)
        self.message_port_register_out(pmt.intern('pdus_out'))

    def handle_msg(self, msg):
        bits = pmt.u8vector_elements(pmt.cdr(msg))
        samples = [-1.0 if bit == 0 else +1.0 for bit in bits]
        pdu = pmt.cons(pmt.PMT_NIL, pmt.init_f32vector(len(samples), samples))
        self.message_port_pub(pmt.intern('pdus_out'), pdu)


class _pdu_receiver(gr.sync_block):
    def __init__(self, frame_size):
        gr.sync_block.__init__(
            self,
            name="_pdu_receiver",
            in_sig=None,
            out_sig=[np.uint8]
        )
        self.frame_size = frame_size
        self.set_output_multiple(self.frame_size)
        self.message_port_register_in(pmt.intern('pdus'))
        self.set_msg_handler(pmt.intern('pdus'), self.handle_msg)
        self.queue = queue.Queue()

    def handle_msg(self, msg):
        values = pmt.u8vector_elements(pmt.cdr(msg))
        self.queue.put(values)

    def work(self, input_items, output_items):
        out0 = output_items[0]
        offset = 0
        while offset < len(out0):
            try:
                values = self.queue.get_nowait()
                out0[offset:offset+self.frame_size] = values
                offset += self.frame_size
            except queue.Empty:
                break
        return offset


class _qa_helper_async(gr.top_block):

    def __init__(self, frame_size, enc, dec, packed, rev_pack):
        gr.top_block.__init__(self, "_qa_helper_async")

        self.enc = enc
        self.dec = dec
        self.frame_size = frame_size
        # These options are for the decoder only. The encoder is always run in
        # unpacked mode.
        self.packed = packed
        self.rev_pack = rev_pack

        self.async_encoder = async_encoder(enc)
        self.async_decoder = async_decoder(
            dec, packed=packed, rev_pack=rev_pack)

        num_frames = 64
        frame_size_bits = 8 * frame_size
        data_in = np.random.randint(
            2, size=frame_size_bits * num_frames, dtype='uint8')
        self.src = blocks.vector_source_b(data_in, False)
        self.pdu_sender = _pdu_sender(frame_size_bits)
        self.pdu_converter = _pdu_converter()
        self.pdu_receiver = _pdu_receiver(frame_size if packed else frame_size_bits)
        self.snk_input = blocks.vector_sink_b()
        self.snk_output = blocks.vector_sink_b()
        if packed:
            self.unpack_decoder = blocks.packed_to_unpacked_bb(
                1, gr.GR_LSB_FIRST if rev_pack else gr.GR_MSB_FIRST)

        self.connect(self.src, self.pdu_sender)
        self.msg_connect((self.pdu_sender, 'pdus'),
                         (self.async_encoder, 'in'))
        self.msg_connect((self.async_encoder, 'out'),
                         (self.pdu_converter, 'pdus_in'))
        self.msg_connect((self.pdu_converter, 'pdus_out'),
                         (self.async_decoder, 'in'))
        self.msg_connect((self.async_decoder, 'out'),
                         (self.pdu_receiver, 'pdus'))
        self.connect(self.src, self.snk_input)
        if packed:
            self.connect(
                self.pdu_receiver, self.unpack_decoder, self.snk_output)
        else:
            self.connect(self.pdu_receiver, self.snk_output)


if __name__ == '__main__':
    frame_size = 30
    enc = fec.dummy_encoder_make(frame_size * 8)
    dec = fec.dummy_decoder.make(frame_size * 8)

    for packed in [True, False]:
        for rev_pack in [True, False]:
            tb = _qa_helper_async(frame_size, enc, dec, packed, rev_pack)
            tb.run()

            errs = 0
            for i, o in zip(tb.snk_input.data(), tb.snk_output.data()):
                if i - o != 0:
                    errs += 1

            if errs == 0:
                print("Decoded properly")
            else:
                print("Problem Decoding")
