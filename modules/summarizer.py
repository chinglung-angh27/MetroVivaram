from transformers import pipeline

class DocumentSummarizer:
    def __init__(self):
        print("Inside summarizer init")
        self.summarizer = pipeline(
            "summarization",
            model="sshleifer/distilbart-cnn-12-6",
            device_map="auto"
        )

    def chunk_text(self, text, max_chars=2000):  # Larger chunks for better context
        sentences = text.split('. ')
        chunks = []
        current_chunk = ''
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 2 <= max_chars:
                current_chunk += sentence + '. '
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    def get_document_insights(self, text, doc_type, filename):
        if not text:
            return {
                "summary": "No text to summarize",
                "action_items": [],
                "deadlines": [],
                "risks": [],
                "priority": "Medium"
            }

        chunks = self.chunk_text(text)
        summaries = []

        for chunk in chunks:
            # Very aggressive summarization - much shorter output
            result = self.summarizer(chunk, max_length=25, min_length=10, do_sample=False)
            raw_summary = result[0]['summary_text'] if result else ""
            if raw_summary.strip():
                summaries.append(f"• {raw_summary.strip()}")

        # Only keep the top 5-7 most important points
        summary = '\n'.join(summaries[:7])

        return {
            "summary": summary,
            "action_items": [],
            "deadlines": [],
            "risks": [],
            "priority": "Medium"
        }
