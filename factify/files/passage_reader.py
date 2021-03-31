class PassageReader:

    def __init__(self, text_file, passage_ids, buffer_size = 1024):
        self.passage_ids_buffer = []
        self.buffer_size = buffer_size
        self.text_file_str = text_file
        self.passage_ids_file_str = passage_ids
        self.i = -1
        self.text_bytes = None

    def __iter__(self):
        return self

    def __enter__(self):
        self.ftext = open(self.text_file_str, "rb")
        self.fpassid = open(self.passage_ids_file_str, "r", encoding="utf8")
        self.fill_buffer()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ftext.close()
        self.fpassid.close()

    def fill_buffer(self):
        count = 0
        has_data_to_read = True
        self.passage_ids_buffer.clear()
        start_offset = -1
        end_offset = -1
        while count < self.buffer_size and has_data_to_read:
            line = next(self.fpassid, None)
            if line is None:
                has_data_to_read = False
            else:
                items = line.split("\t")
                if len(self.passage_ids_buffer) == 0:
                    start_offset = int(items[1])
                else:
                    end_offset = int(items[2])

                self.passage_ids_buffer.append([items[0], int(items[1])-start_offset, int(items[2])-start_offset])
                count += 1

        self.buffer_size = count
        if count == 0:
            self.i = 0
            return
        self.ftext.seek(start_offset)
        self.text_bytes = self.ftext.read(end_offset-start_offset)
        self.i = -1

    def __next__(self):
        if self.i == self.buffer_size-1 and self.buffer_size != 0:
            self.fill_buffer()

        if self.buffer_size == 0:
            raise StopIteration()

        self.i += 1
        passage_triple = self.passage_ids_buffer[self.i]

        return passage_triple[0], self.text_bytes[passage_triple[1]:passage_triple[2]].decode("utf8")

    def close(self):
        self.fpassid.close()
        self.ftext.close()
