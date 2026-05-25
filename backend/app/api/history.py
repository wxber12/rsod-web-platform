from fastapi import APIRouter, HTTPException, Query
from database import get_db_connection
from psycopg2.extras import RealDictCursor
from app.models.schemas import HistoryResponse, HistoryDetailResponse

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/", response_model=HistoryResponse)
async def get_history(limit: int = Query(20), offset: int = Query(0)):
    """获取检测历史记录"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT detection_id, type, original_url as image_url, result_url as result_image_url, 
                   total_objects, detection_time, model_name, created_at
            FROM detection_history 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        history = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return HistoryResponse(
            success=True,
            message="获取历史记录成功",
            data=history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")


@router.get("/{detection_id}", response_model=HistoryDetailResponse)
async def get_history_detail(detection_id: str):
    """获取指定检测详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT detection_id, type, original_url as image_url, result_url as result_image_url, 
                   total_objects, detection_time, model_name, created_at
            FROM detection_history 
            WHERE detection_id = %s
        """, (detection_id,))
        
        detail = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not detail:
            raise HTTPException(status_code=404, detail="未找到该检测记录")
            
        return HistoryDetailResponse(
            success=True,
            message="获取详情成功",
            data=detail
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取详情失败: {str(e)}")
