from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DetectionBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int
    class_name: str


class DetectionResult(BaseModel):
    detection_id: str
    image_url: str
    result_image_url: str
    boxes: List[DetectionBox]
    total_objects: int
    detection_time: float
    model_name: str
    created_at: datetime


class SingleDetectionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[DetectionResult] = None


class BatchDetectionResponse(BaseModel):
    success: bool
    message: str
    data: List[DetectionResult]


class VideoDetectionResult(BaseModel):
    detection_id: str
    video_url: str
    result_video_url: str
    total_frames: int
    detection_time: float
    model_name: str
    created_at: datetime


class VideoDetectionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[VideoDetectionResult] = None


class HistoryItem(BaseModel):
    detection_id: str
    type: str
    image_url: str
    result_image_url: str
    total_objects: int
    detection_time: float
    model_name: str
    created_at: datetime


class HistoryResponse(BaseModel):
    success: bool
    message: str
    data: List[HistoryItem]
    total: Optional[int] = 0


class HistoryDetailResponse(BaseModel):
    success: bool
    message: str
    data: Optional[HistoryItem] = None


class TargetItem(BaseModel):
    id: int
    name: str
    count: int
    icon: str


class TargetListResponse(BaseModel):
    success: bool
    message: str
    data: List[TargetItem]


class ChatRequest(BaseModel):
    question: str
    history: Optional[List[dict]] = []


class ChatResponse(BaseModel):
    success: bool
    message: str
    answer: str