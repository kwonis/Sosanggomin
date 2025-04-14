# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv
import os
import platform

# 라우터 
from routers import chat_router, news_router, data_analysis_router, s3_router, data_router, eda_router, review_router, store_router, competitor_router, area_analysis_router, final_report_router, location_recommendation_router

# 스케줄러 
from schedulers.news_scheduler import start_news_scheduler
from schedulers.area_analysis_scheduler import start_area_scheduler
from schedulers.transport_scheduler import start_subway_station_scheduler
from schedulers.weather_scheduler import start_weather_scheduler

is_windows = platform.system() == "Windows"
if not is_windows:
    import fcntl

# 환경 변수 로드
load_dotenv("./config/.env")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="소상공인 데이터 분석 플랫폼 API",
    description="소상공인을 위한, 데이터 분석, 예측, 채팅 및 뉴스 API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router.router)
app.include_router(news_router.router)
app.include_router(data_analysis_router.router)
app.include_router(s3_router.router)
app.include_router(data_router.router)
app.include_router(eda_router.router)
app.include_router(review_router.router)
app.include_router(store_router.router)
app.include_router(competitor_router.router)
app.include_router(area_analysis_router.router)
app.include_router(final_report_router.router)
app.include_router(location_recommendation_router.router)

@app.get("/")
def read_root():
    return {"message": "소상공인을 위한 API 서비스가 실행 중입니다."}

@app.on_event("startup")
async def startup_event():
    if is_windows:
        # Windows 환경에서는 스케줄러를 단순히 시작
        logger.info("Windows 환경에서 스케줄러 시작 (파일 잠금 없음)")
        start_news_scheduler()
        logger.info("애플리케이션 시작 및 뉴스 업데이트 작업 스케줄링 완료")
        start_area_scheduler()
        logger.info("상권분석 스케줄링 완료")
        start_subway_station_scheduler()
        logger.info("지하철역/버스 정류장 위치 정보 스케줄링 완료")
        # start_weather_scheduler()
        # logger.info("날씨 데이터 수집 스케줄링 완료")
        return
    
    # Linux/Unix 환경
    lock_file_path = "/tmp/scheduler.lock"
    
    try:
        lock_file = open(lock_file_path, "w+")
        
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            logger.info("메인 프로세스로 스케줄러 시작")
            
            start_news_scheduler()
            logger.info("애플리케이션 시작 및 뉴스 업데이트 작업 스케줄링 완료")

            start_area_scheduler()
            logger.info("상권분석 스케줄링 완료")
        
            start_subway_station_scheduler()
            logger.info("지하철역/버스 정류장 위치 정보 스케줄링 완료")

            # start_weather_scheduler()
            # logger.info("날씨 데이터 수집 스케줄링 완료")
            
            app.state.lock_file = lock_file
            
        except IOError:
            lock_file.close()
            logger.info("다른 프로세스가 이미 스케줄러를 실행 중입니다.")
    
    except Exception as e:
        logger.error(f"스케줄러 시작 중 오류 발생: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    if is_windows:
        logger.info("Windows 환경에서 애플리케이션 종료")
        return
        
    if hasattr(app.state, "lock_file"):
        try:
            fcntl.flock(app.state.lock_file, fcntl.LOCK_UN)
            app.state.lock_file.close()
            logger.info("스케줄러 락 해제 완료")
        except Exception as e:
            logger.error(f"스케줄러 락 해제 중 오류 발생: {e}")
    
    logger.info("애플리케이션 종료")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)