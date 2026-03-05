"""
/**
 * [IN]: 标准 Python 异常基类
 * [OUT]: DeepRead 项目统一异常类体系
 * [POS]: 被所有模块使用，用于错误分类和处理
 * [PROTOCOL]: 新增错误码 -> 同步更新本文件和错误处理文档
 */
"""


class DeepReadError(Exception):
    """DeepRead 项目基础异常类"""

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "ERR_UNKNOWN"
        self.details = details or {}

    def __str__(self):
        if self.details:
            return f"[{self.error_code}] {self.message} - Details: {self.details}"
        return f"[{self.error_code}] {self.message}"


# ========== PDF 相关异常 ==========

class PDFAccessError(DeepReadError):
    """PDF 文件访问错误"""
    pass


class PDFNotFoundError(PDFAccessError):
    """PDF 文件不存在"""

    def __init__(self, file_path: str):
        super().__init__(
            message=f"PDF file not found: {file_path}",
            error_code="ERR_PDF_NOT_FOUND",
            details={"file_path": file_path}
        )


class PDFCorruptedError(PDFAccessError):
    """PDF 文件损坏或格式无效"""

    def __init__(self, file_path: str, reason: str = ""):
        super().__init__(
            message=f"PDF file is corrupted or invalid: {file_path}. {reason}",
            error_code="ERR_PDF_CORRUPTED",
            details={"file_path": file_path, "reason": reason}
        )


class PDFEncryptedError(PDFAccessError):
    """PDF 文件加密且无法解密"""

    def __init__(self, file_path: str):
        super().__init__(
            message=f"PDF is password protected: {file_path}",
            error_code="ERR_PDF_ENCRYPTED",
            details={"file_path": file_path}
        )


class PDFEmptyError(PDFAccessError):
    """PDF 文件页数为 0"""

    def __init__(self, file_path: str):
        super().__init__(
            message=f"PDF has no pages: {file_path}",
            error_code="ERR_PDF_EMPTY",
            details={"file_path": file_path}
        )


class PDFTooLargeError(PDFAccessError):
    """PDF 文件过大"""

    def __init__(self, file_path: str, page_count: int, max_pages: int = 500):
        super().__init__(
            message=f"PDF too large: {page_count} pages (max {max_pages})",
            error_code="ERR_PDF_TOO_LARGE",
            details={"file_path": file_path, "page_count": page_count, "max_pages": max_pages}
        )


# ========== Marker 处理异常 ==========

class MarkerProcessingError(DeepReadError):
    """Marker PDF 转换错误"""
    pass


class MarkerTimeoutError(MarkerProcessingError):
    """Marker 处理超时"""

    def __init__(self, file_path: str, timeout_seconds: int):
        super().__init__(
            message=f"Marker processing timeout after {timeout_seconds}s: {file_path}",
            error_code="ERR_MARKER_TIMEOUT",
            details={"file_path": file_path, "timeout": timeout_seconds}
        )


class TitleExtractError(MarkerProcessingError):
    """标题提取失败"""

    def __init__(self, file_path: str, reason: str = ""):
        super().__init__(
            message=f"Failed to extract title from PDF: {file_path}. {reason}",
            error_code="ERR_TITLE_EXTRACT_FAILED",
            details={"file_path": file_path, "reason": reason}
        )


# ========== LLM 相关异常 ==========

class LLMRequestError(DeepReadError):
    """LLM API 请求错误"""
    pass


class LLMTimeoutError(LLMRequestError):
    """LLM 请求超时"""

    def __init__(self, model: str, timeout_seconds: int):
        super().__init__(
            message=f"LLM request timeout after {timeout_seconds}s: {model}",
            error_code="ERR_LLM_TIMEOUT",
            details={"model": model, "timeout": timeout_seconds}
        )


class LLMRateLimitError(LLMRequestError):
    """LLM API 速率限制"""

    def __init__(self, model: str, retry_after: int = None):
        super().__init__(
            message=f"LLM rate limit exceeded: {model}",
            error_code="ERR_LLM_RATE_LIMIT",
            details={"model": model, "retry_after": retry_after}
        )


class LLMAuthenticationError(LLMRequestError):
    """LLM API 认证失败"""

    def __init__(self, model: str):
        super().__init__(
            message=f"LLM authentication failed. Check your API_KEY.",
            error_code="ERR_LLM_AUTH",
            details={"model": model}
        )


class LLMInvalidResponseError(LLMRequestError):
    """LLM 返回无效响应"""

    def __init__(self, model: str, reason: str = ""):
        super().__init__(
            message=f"LLM returned invalid response: {reason}",
            error_code="ERR_LLM_INVALID_RESPONSE",
            details={"model": model, "reason": reason}
        )


class LLMInvalidJSONError(LLMRequestError):
    """LLM 返回无效 JSON"""

    def __init__(self, model: str, raw_response: str = ""):
        super().__init__(
            message="LLM returned invalid JSON format",
            error_code="ERR_LLM_INVALID_JSON",
            details={"model": model, "raw_response_preview": raw_response[:200]}
        )


class LLMValidationError(LLMRequestError):
    """LLM 返回内容结构验证失败"""

    def __init__(self, message: str, raw_response: str = "", missing_fields: list = None):
        super().__init__(
            message=message,
            error_code="ERR_LLM_VALIDATION",
            details={
                "raw_response_preview": raw_response[:200] if raw_response else "",
                "missing_fields": missing_fields or []
            }
        )


# ========== Canvas 相关异常 ==========

class CanvasLayoutError(DeepReadError):
    """Canvas 布局错误"""
    pass


class CanvasGenerationError(CanvasLayoutError):
    """Canvas 生成失败"""

    def __init__(self, file_path: str, reason: str = ""):
        super().__init__(
            message=f"Failed to generate canvas: {file_path}. {reason}",
            error_code="ERR_CANVAS_GENERATION",
            details={"file_path": file_path, "reason": reason}
        )


# ========== 配置相关异常 ==========

class ConfigError(DeepReadError):
    """配置错误"""
    pass


class ConfigValidationError(ConfigError):
    """配置验证失败"""

    def __init__(self, errors: list[str]):
        super().__init__(
            message=f"Configuration validation failed: {'; '.join(errors)}",
            error_code="ERR_CONFIG_INVALID",
            details={"errors": errors}
        )


# ========== 状态追踪相关异常 ==========

class StateTrackerError(DeepReadError):
    """状态追踪错误"""
    pass


class StateFileCorruptedError(StateTrackerError):
    """state.json 文件损坏"""

    def __init__(self, reason: str = ""):
        super().__init__(
            message=f"State file is corrupted: {reason}",
            error_code="ERR_STATE_CORRUPTED",
            details={"reason": reason}
        )
