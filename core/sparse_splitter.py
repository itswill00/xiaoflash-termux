import os
import struct

class SparseSplitter:
    """Android Sparse Image & RAW Image Splitter for High-Speed OTG Flashing"""

    @staticmethod
    def is_sparse(file_path):
        if not os.path.exists(file_path):
            return False
        try:
            with open(file_path, "rb") as f:
                magic_bin = f.read(4)
                return magic_bin == b'\x3a\xff\x26\xed'
        except:
            return False

    @staticmethod
    def split_raw_file(file_path, max_size=300 * 1024 * 1024, blk_sz=4096):
        """Splits a RAW file (e.g. non-sparse userdata.img) into valid sub-sparse chunk files <= max_size"""
        if not os.path.exists(file_path):
            return [file_path]

        file_size = os.path.getsize(file_path)
        if file_size <= max_size:
            return [file_path]

        sub_files = []
        sub_idx = 0

        with open(file_path, "rb") as f_in:
            while True:
                chunk_data = f_in.read(max_size)
                if not chunk_data:
                    break

                raw_len = len(chunk_data)
                remainder = raw_len % blk_sz
                if remainder != 0:
                    chunk_data += b'\x00' * (blk_sz - remainder)
                    raw_len = len(chunk_data)

                c_blks = raw_len // blk_sz
                file_hdr = struct.pack('<IHHHHIIII', 0xed26ff3a, 1, 0, 28, 12, blk_sz, c_blks, 1, 0)
                chunk_hdr = struct.pack('<HHII', 0xCAC1, 0, c_blks, raw_len + 12)

                out_p = f"{file_path}.sparse_raw_part{sub_idx}"
                with open(out_p, "wb") as out_f:
                    out_f.write(file_hdr)
                    out_f.write(chunk_hdr)
                    out_f.write(chunk_data)

                sub_files.append(out_p)
                sub_idx += 1

        return sub_files if len(sub_files) > 1 else [file_path]

    @staticmethod
    def split_sparse_file(file_path, max_size=300 * 1024 * 1024):
        """
        Splits an Android Sparse Image (.img) or RAW image into sub-sparse images <= max_size
        Returns a list of file paths (either original or temporary sub-sparse files)
        """
        if not os.path.exists(file_path) or os.path.getsize(file_path) <= max_size:
            return [file_path]

        if not SparseSplitter.is_sparse(file_path):
            return SparseSplitter.split_raw_file(file_path, max_size=max_size)

        try:
            with open(file_path, 'rb') as f:
                magic_bin = f.read(4)
                header_bin = f.read(24)
                magic, major, minor, file_hdr_sz, chunk_hdr_sz, blk_sz, total_blks, total_chunks, crc = struct.unpack('<IHHHHIIII', magic_bin + header_bin)

                sub_files = []
                curr_chunks = []
                curr_blks = 0
                curr_sz = 28
                sub_idx = 0

                for i in range(total_chunks):
                    c_hdr_bin = f.read(chunk_hdr_sz)
                    c_type, res, c_blks, c_tot_sz = struct.unpack('<HHII', c_hdr_bin)
                    payload_sz = c_tot_sz - chunk_hdr_sz
                    payload = f.read(payload_sz)

                    if c_type == 0xCAC1 and c_tot_sz > max_size:
                        sub_raw_max = max_size - 100
                        sub_blks_sz = sub_raw_max // blk_sz
                        sub_bytes = sub_blks_sz * blk_sz

                        offset = 0
                        while offset < payload_sz:
                            sub_p = payload[offset:offset+sub_bytes]
                            sub_b = len(sub_p) // blk_sz
                            sub_h = struct.pack('<HHII', 0xCAC1, 0, sub_b, len(sub_p) + 12)
                            sub_tot = len(sub_p) + 12

                            if curr_sz + sub_tot > max_size and curr_chunks:
                                out_p = f"{file_path}.sparse_part{sub_idx}"
                                with open(out_p, 'wb') as out_f:
                                    out_f.write(struct.pack('<IHHHHIIII', magic, major, minor, file_hdr_sz, chunk_hdr_sz, blk_sz, curr_blks, len(curr_chunks), 0))
                                    for ch_h, ch_p in curr_chunks:
                                        out_f.write(ch_h)
                                        out_f.write(ch_p)
                                sub_files.append(out_p)
                                sub_idx += 1
                                curr_chunks = []
                                curr_blks = 0
                                curr_sz = 28

                            curr_chunks.append((sub_h, sub_p))
                            curr_blks += sub_b
                            curr_sz += sub_tot
                            offset += len(sub_p)
                    else:
                        if curr_sz + c_tot_sz > max_size and curr_chunks:
                            out_p = f"{file_path}.sparse_part{sub_idx}"
                            with open(out_p, 'wb') as out_f:
                                out_f.write(struct.pack('<IHHHHIIII', magic, major, minor, file_hdr_sz, chunk_hdr_sz, blk_sz, curr_blks, len(curr_chunks), 0))
                                for ch_h, ch_p in curr_chunks:
                                    out_f.write(ch_h)
                                    out_f.write(ch_p)
                            sub_files.append(out_p)
                            sub_idx += 1
                            curr_chunks = []
                            curr_blks = 0
                            curr_sz = 28

                        curr_chunks.append((c_hdr_bin, payload))
                        curr_blks += c_blks
                        curr_sz += c_tot_sz

                if curr_chunks:
                    out_p = f"{file_path}.sparse_part{sub_idx}"
                    with open(out_p, 'wb') as out_f:
                        out_f.write(struct.pack('<IHHHHIIII', magic, major, minor, file_hdr_sz, chunk_hdr_sz, blk_sz, curr_blks, len(curr_chunks), 0))
                        for ch_h, ch_p in curr_chunks:
                            out_f.write(ch_h)
                            out_f.write(ch_p)
                    sub_files.append(out_p)

                return sub_files if len(sub_files) > 1 else [file_path]

        except Exception:
            return [file_path]
