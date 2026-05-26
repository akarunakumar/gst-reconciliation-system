from app.orchestration.base_agent import AgentResult, BaseAgent

ALLOWED_EXTENSIONS = {".xlsx", ".xls"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class FileUploadAgent(BaseAgent):
    """Validates file type and size; passes raw bytes into context."""

    def run(self, context: dict) -> AgentResult:
        filename: str = context.get("filename", "")
        file_bytes: bytes = context.get("file_bytes", b"")

        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            return AgentResult(success=False, errors=[f"Unsupported file type '{ext}'. Allowed: .xlsx, .xls"])

        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            mb = len(file_bytes) / (1024 * 1024)
            return AgentResult(success=False, errors=[f"File size {mb:.1f} MB exceeds 10 MB limit"])

        return AgentResult(success=True, data={"filename": filename, "file_bytes": file_bytes})
