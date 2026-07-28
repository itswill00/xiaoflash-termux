import os
import struct

class SparseSplitter:
    """Android Sparse Image Splitter for High-Speed OTG Flashing"""

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
    def split_sparse_file(file_path, max_size=300 * 1024 * 1024):
        """
        Splits an Android Sparse Image (.img) into sub-sparse images <= max_size
        Returns a list of file paths (either original or temporary sub-sparse files)
        """
        if not SparseSplitter.is_sparse(file_path) or os.path.getsize(file_path) <= max_size:
            return [file_path]

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
