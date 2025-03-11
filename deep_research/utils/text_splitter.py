from abc import ABC, abstractmethod


class TextSplitter(ABC):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("Cannot have chunk_overlap >= chunk_size")

    @abstractmethod
    def split_text(self, text: str) -> list:
        pass

    def create_documents(self, texts: list) -> list:
        documents = []
        for text in texts:
            for chunk in self.split_text(text):
                documents.append(chunk)
        return documents

    def split_documents(self, documents: list) -> list:
        return self.create_documents(documents)

    def _join_docs(self, docs: list, separator: str) -> str:
        text = separator.join(docs).strip()
        return text if text else None

    def merge_splits(self, splits: list, separator: str) -> list:
        docs = []
        current_doc = []
        total = 0
        for d in splits:
            _len = len(d)
            if total + _len >= self.chunk_size:
                if total > self.chunk_size:
                    print(f"Warning: Created a chunk of size {total}, which is longer than the specified {self.chunk_size}")
                if current_doc:
                    doc = self._join_docs(current_doc, separator)
                    if doc is not None:
                        docs.append(doc)
                    while current_doc and (total > self.chunk_overlap or (total + _len > self.chunk_size and total > 0)):
                        total -= len(current_doc[0])
                        current_doc.pop(0)
            current_doc.append(d)
            total += _len
        doc = self._join_docs(current_doc, separator)
        if doc is not None:
            docs.append(doc)
        return docs


class RecursiveCharacterTextSplitter(TextSplitter):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, separators: list = None):
        super().__init__(chunk_size, chunk_overlap)
        self.separators = separators if separators is not None else ['\n\n', '\n', '.', ',', '>', '<', ' ', '']

    def split_text(self, text: str) -> list:
        final_chunks = []
        # Choose an appropriate separator.
        separator = self.separators[-1]
        for s in self.separators:
            if s == "":
                separator = s
                break
            if s in text:
                separator = s
                break

        # Split the text.
        splits = text.split(separator) if separator != "" else list(text)
        good_splits = []
        for s in splits:
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if good_splits:
                    merged = self.merge_splits(good_splits, separator)
                    final_chunks.extend(merged)
                    good_splits = []
                other_info = self.split_text(s)
                final_chunks.extend(other_info)
        if good_splits:
            merged = self.merge_splits(good_splits, separator)
            final_chunks.extend(merged)
        return final_chunks
