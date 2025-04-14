# models.py
import os
import logging
import datetime
from sqlalchemy import create_engine, event, Column, String, DateTime, Integer, Text, ForeignKey, Date, Enum, Float, BigInteger, INTEGER, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# 로깅 설정
logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    social_id = Column(Integer, nullable=True)
    user_type = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    profileImgUrl = Column(String(1023), nullable=True)
    user_role = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

class News(Base):
    __tablename__ = 'news'
    news_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    link = Column(Text, nullable=False)
    pub_date = Column(Date, nullable=False)
    image_url = Column(Text)
    category = Column(String(50), nullable=False)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    uid = Column(String(36), primary_key=True)
    user_id = Column(Integer)  
    created_at = Column(DateTime(timezone=True)) 
    updated_at = Column(DateTime(timezone=True))  
    conversations = relationship("ChatHistory", back_populates="session")

class ChatHistory(Base):
    __tablename__ = 'chat_histories'
    index = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), ForeignKey('chat_sessions.uid'))
    user_id = Column(Integer)
    user_message = Column(Text)
    bot_message = Column(Text)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))  
    session = relationship("ChatSession", back_populates="conversations")  

class Weathers(Base):
    __tablename__ = 'weathers'

    weather_id = Column(Integer, primary_key=True, autoincrement=True, comment='날씨 데이터 ID (PK)')
    datetime = Column(Integer, unique=True, comment='YYYYMMDDHH 형식의 단일 datetime 키')
    year = Column(String(4), comment='연도 (YYYY)')
    month = Column(String(2), comment='월 (MM, 두 자리)')
    day = Column(String(2), comment='일 (DD, 두 자리)')
    hour = Column(String(2), nullable=False, comment='시간 (HH, 두 자리)')
    location = Column(String(20), comment='지역명 (예: 서울)')
    
    ta = Column(Float, nullable=True, comment='기온 (°C)')
    ws = Column(Float, nullable=True, comment='풍속 (m/s)')
    hm = Column(Float, nullable=True, comment='습도 (%)')
    rn = Column(Float, nullable=True, comment='강수량 (mm)')

class Store(Base):
    __tablename__ = 'stores'
    
    store_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    store_name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    place_id = Column(String(100), nullable=False)
    category = Column(String(100))
    review_count = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    pos_type = Column(String(255))
    business_number = Column(String(12), nullable=True, comment="사업자등록번호")
    is_verified = Column(Boolean, default=False, nullable=False, comment="사업자번호 인증 여부")
    is_main = Column(Boolean, default=False, nullable=False, comment="사용자의 대표 가게 여부")
    
class SubwayStation(Base):
    __tablename__ = "subway_stations"

    station_id = Column(Integer, primary_key=True, autoincrement=True, comment="지하철역 데이터 ID (PK)")
    bldn_id = Column(String(20), unique=True, nullable=False, comment="역사 ID")
    station_name = Column(String(100), nullable=False, comment="역사명")
    route = Column(String(50), nullable=False, comment="호선")
    latitude = Column(Float, nullable=False, comment="위도")
    longitude = Column(Float, nullable=False, comment="경도")
    created_at = Column(DateTime, default=datetime.datetime.now, comment="데이터 수집 시점")

class BusStop(Base):
    __tablename__ = "bus_stops"

    stop_id = Column(Integer, primary_key=True, autoincrement=True, comment="정류소 데이터 ID (PK)")
    stop_no = Column(String(20), unique=True, nullable=False, comment="정류소 번호")
    stop_name = Column(String(100), nullable=False, comment="정류소 이름")
    longitude = Column(Float, nullable=False, comment="경도")
    latitude = Column(Float, nullable=False, comment="위도")
    node_id = Column(String(50), nullable=True, comment="노드 ID")
    stop_type = Column(String(50), nullable=True, comment="정류소 타입")
    created_at = Column(DateTime, default=datetime.datetime.now, comment="데이터 수집 시점")


class Population(Base):
    __tablename__ = 'populations' 

    population_id = Column(Integer, primary_key=True, autoincrement=True, comment='인구 데이터 ID (PK)')

    district_name = Column(String(45), comment='구 이름')
    region_name = Column(String(45), comment='동 이름')

    ## 유동인구 
    # stdr_yyqu_cd = Column(String(6), comment='기준 년월분기 코드 (예: 202301)', nullable=False)
    # adstrd_cd_nm = Column(String(100), comment='행정동 코드명 (예: 강남구 역삼동)', nullable=False)

    # 남성 연령대별 인구
    male_10_fpop = Column(Integer, nullable=True, comment='남성연령대_10_인구 수')
    male_20_fpop  = Column(Integer, nullable=True, comment='남성연령대_20_인구 수')
    male_30_fpop  = Column(Integer, nullable=True, comment='남성연령대_30_인구 수')
    male_40_fpop  = Column(Integer, nullable=True, comment='남성연령대_40_인구 수')
    male_50_fpop  = Column(Integer, nullable=True, comment='남성연령대_50_인구 수')
    male_60_fpop  = Column(Integer, nullable=True, comment='남성연령대_60이상_인구 수')

    # 여성 연령대별 인구
    female_10_fpop = Column(Integer, nullable=True, comment='여성연령대_10_인구 수')
    female_20_fpop = Column(Integer, nullable=True, comment='여성연령대_20_인구 수')
    female_30_fpop = Column(Integer, nullable=True, comment='여성연령대_30_인구 수')
    female_40_fpop = Column(Integer, nullable=True, comment='여성연령대_40_인구 수')
    female_50_fpop = Column(Integer, nullable=True, comment='여성연령대_50_인구 수')
    female_60_fpop = Column(Integer, nullable=True, comment='여성연령대_60이상_인구 수')

    # 시간대 유동인구
    late_night_fpop = Column(Integer)
    early_morning_fpop = Column(Integer)
    morning_peak_fpop = Column(Integer)
    afternoon_fpop = Column(Integer)
    midday_fpop = Column(Integer)
    evening_peak_fpop = Column(Integer)
    night_fpop = Column(Integer)

    # 요일별 유동인구
    monday_fpop = Column(Integer)
    tuesday_fpop = Column(Integer)
    wednesday_fpop = Column(Integer)
    thursday_fpop = Column(Integer)
    friday_fpop = Column(Integer)
    saturday_fpop = Column(Integer)
    sunday_fpop = Column(Integer)

    # 기타 유동인구 정보
    purpose_1_fpop = Column(String(45))
    purpose_2_fpop = Column(String(45))
    purpose_3_fpop = Column(String(45))
    dominant_age_gender_fpop = Column(String(45))
    minor_age_gender_fpop = Column(String(45))
    busiest_hour_fpop = Column(String(45))
    quietest_hour_fpop = Column(String(45))
    busiest_day_fpop = Column(String(45))
    quietest_day_fpop = Column(String(45))
    weekday_avg_fpop = Column(Float)
    weekend_avg_fpop = Column(Float)

    # 총 인구
    tot_fpop = Column(Integer, nullable=True, comment='총 인구 수')

    ## 상주인구
    # stdr_yyqu_cd = Column(String(6), comment='기준 년월분기 코드 (예: 202301)', nullable=False)
    # adstrd_cd_nm = Column(String(100), comment='행정동 코드명 (예: 강남구 역삼동)', nullable=False)

    # 총 인구
    tot_repop = Column(Integer, nullable=True, comment='총 인구 수')

    # 남성 연령대별 인구
    male_10_repop = Column(Integer, nullable=True, comment='남성연령대_10_인구 수')
    male_20_repop  = Column(Integer, nullable=True, comment='남성연령대_20_인구 수')
    male_30_repop  = Column(Integer, nullable=True, comment='남성연령대_30_인구 수')
    male_40_repop  = Column(Integer, nullable=True, comment='남성연령대_40_인구 수')
    male_50_repop  = Column(Integer, nullable=True, comment='남성연령대_50_인구 수')
    male_60_repop  = Column(Integer, nullable=True, comment='남성연령대_60이상_인구 수')

    # 여성 연령대별 인구
    female_10_repop = Column(Integer, nullable=True, comment='여성연령대_10_인구 수')
    female_20_repop = Column(Integer, nullable=True, comment='여성연령대_20_인구 수')
    female_30_repop = Column(Integer, nullable=True, comment='여성연령대_30_인구 수')
    female_40_repop = Column(Integer, nullable=True, comment='여성연령대_40_인구 수')
    female_50_repop = Column(Integer, nullable=True, comment='여성연령대_50_인구 수')
    female_60_repop = Column(Integer, nullable=True, comment='여성연령대_60이상_인구 수')

    dominant_age_gender_repop=Column(String(45))
    minor_age_gender_repop=Column(String(45))

    ## 직장인구
    # stdr_yyqu_cd = Column(String(6), comment='기준 년월분기 코드 (예: 202301)', nullable=False)
    # adstrd_cd_nm = Column(String(100), comment='행정동 코드명 (예: 강남구 역삼동)', nullable=False)

    # 총 인구
    tot_wrpop = Column(Integer, nullable=True, comment='총 인구 수')

    # 남성 연령대별 인구
    male_10_wrpop = Column(Integer, nullable=True, comment='남성연령대_10_인구 수')
    male_20_wrpop  = Column(Integer, nullable=True, comment='남성연령대_20_인구 수')
    male_30_wrpop  = Column(Integer, nullable=True, comment='남성연령대_30_인구 수')
    male_40_wrpop  = Column(Integer, nullable=True, comment='남성연령대_40_인구 수')
    male_50_wrpop  = Column(Integer, nullable=True, comment='남성연령대_50_인구 수')
    male_60_wrpop  = Column(Integer, nullable=True, comment='남성연령대_60이상_인구 수')

    # 여성 연령대별 인구
    female_10_wrpop = Column(Integer, nullable=True, comment='여성연령대_10_인구 수')
    female_20_wrpop = Column(Integer, nullable=True, comment='여성연령대_20_인구 수')
    female_30_wrpop = Column(Integer, nullable=True, comment='여성연령대_30_인구 수')
    female_40_wrpop = Column(Integer, nullable=True, comment='여성연령대_40_인구 수')
    female_50_wrpop = Column(Integer, nullable=True, comment='여성연령대_50_인구 수')
    female_60_wrpop = Column(Integer, nullable=True, comment='여성연령대_60이상_인구 수')

    dominant_age_gender_wrpop=Column(String(45))
    minor_age_gender_wrpop=Column(String(45))

    # 등록 일시
    created_at = Column(DateTime, default=datetime.datetime.now(), comment='데이터 수집 시점')


class StoreCategories(Base):
    __tablename__ = "store_categories"

    store_statistic_id = Column(Integer, primary_key=True, autoincrement=True)

    # 날짜 기준
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)

    # 지역 정보
    district_name = Column(String(50))        # 자치구
    region_name = Column(String(100))         # 행정동
    industry_name = Column(String(100))       # 업종명
    main_category = Column(String(50))        # 대분류

    # 점포 관련 수치
    store_count = Column(Integer)
    main_category_total = Column(Integer)

    open_rate = Column(Float)
    open_store_count = Column(Integer)
    close_rate = Column(Float)
    close_store_count = Column(Integer)

    # 상권 변화 지표 관련
    ta_change_index = Column(String(2), nullable=True)                    # TRDAR_CHNGE_IX
    ta_change_index_name = Column(String(100), nullable=True)         # TRDAR_CHNGE_IX_NM

    open_sales_month_avg = Column(Float, nullable=True)               # OPR_SALE_MT_AVRG
    close_sales_month_avg = Column(Float, nullable=True)             # CLS_SALE_MT_AVRG
    seoul_open_sales_month_avg = Column(Float, nullable=True)         # SU_OPR_SALE_MT_AVRG
    seoul_close_sales_month_avg = Column(Float, nullable=True)       # SU_CLS_SALE_MT_AVRG

    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

class SalesData(Base):
    __tablename__ = "sales_data"

    sale_id = Column(Integer, primary_key=True, autoincrement=True)

    # 기본 정보
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    district_name = Column(String(50), nullable=False)
    region_name = Column(String(50), nullable=False)
    industry_name = Column(String(100), nullable=False)
    main_category = Column(String(50), nullable=False)

    # 전체 매출 금액/건수
    sales_amount = Column(BigInteger, default=0)
    sales_count = Column(Integer, default=0)

    # 요일별 매출 금액
    weekday_sales_amount = Column(BigInteger, default=0)
    weekend_sales_amount = Column(BigInteger, default=0)
    mon_sales_amount = Column(BigInteger, default=0)
    tues_sales_amount = Column(BigInteger, default=0)
    wed_sales_amount = Column(BigInteger, default=0)
    thur_sales_amount = Column(BigInteger, default=0)
    fri_sales_amount = Column(BigInteger, default=0)
    sat_sales_amount = Column(BigInteger, default=0)
    sun_sales_amount = Column(BigInteger, default=0)

    # 시간대별 매출 금액
    time_00_06_sales_amount = Column(BigInteger, default=0)
    time_06_11_sales_amount = Column(BigInteger, default=0)
    time_11_14_sales_amount = Column(BigInteger, default=0)
    time_14_17_sales_amount = Column(BigInteger, default=0)
    time_17_21_sales_amount = Column(BigInteger, default=0)
    time_21_24_sales_amount = Column(BigInteger, default=0)

    # 성별 매출 금액
    male_sales_amount = Column(BigInteger, default=0)
    female_sales_amount = Column(BigInteger, default=0)

    # 연령대 매출 금액
    age_10_sales_amount = Column(BigInteger, default=0)
    age_20_sales_amount = Column(BigInteger, default=0)
    age_30_sales_amount = Column(BigInteger, default=0)
    age_40_sales_amount = Column(BigInteger, default=0)
    age_50_sales_amount = Column(BigInteger, default=0)
    age_60_sales_amount = Column(BigInteger, default=0)

    # 요일별 매출 건수
    weekday_sales_count = Column(Integer, default=0)
    weekend_sales_count = Column(Integer, default=0)
    mon_sales_count = Column(Integer, default=0)
    tues_sales_count = Column(Integer, default=0)
    wed_sales_count = Column(Integer, default=0)
    thur_sales_count = Column(Integer, default=0)
    fri_sales_count = Column(Integer, default=0)
    sat_sales_count = Column(Integer, default=0)
    sun_sales_count = Column(Integer, default=0)

    # 시간대별 매출 건수
    time_00_06_sales_count = Column(Integer, default=0)
    time_06_11_sales_count = Column(Integer, default=0)
    time_11_14_sales_count = Column(Integer, default=0)
    time_14_17_sales_count = Column(Integer, default=0)
    time_17_21_sales_count = Column(Integer, default=0)
    time_21_24_sales_count = Column(Integer, default=0)

    # 성별 매출 건수
    male_sales_count = Column(Integer, default=0)
    female_sales_count = Column(Integer, default=0)

    # 연령대 매출 건수
    age_10_sales_count = Column(Integer, default=0)
    age_20_sales_count = Column(Integer, default=0)
    age_30_sales_count = Column(Integer, default=0)
    age_40_sales_count = Column(Integer, default=0)
    age_50_sales_count = Column(Integer, default=0)
    age_60_sales_count = Column(Integer, default=0)

class RentInfo(Base):
    __tablename__ = "rent_info"

    STRD_YR_CD = Column(String(4), primary_key=True, comment="기준년코드")
    STRD_QTR_CD = Column(String(1), primary_key=True, comment="기준분기코드")
    ADSTRD_CD = Column(String(10), primary_key=True, comment="행정동코드")
    LET_CURPRC_FLR_CLSF_CD = Column(String(10), primary_key=True, comment="임대시세층구분코드")

    ADSTRD_CD_NM = Column(String(255), nullable=True, comment="행정동코드명")
    LET_CURPRC_FLR_CLSF_CD_NM = Column(String(10), nullable=True, comment="임대시세층구분명")
    GTN_AVE = Column(Integer, nullable=True, comment="보증금평균")
    MNTH_RENTCG_AVE = Column(Integer, nullable=True, comment="월임대료평균")
    EXCHE_RENTCG_AVE = Column(Integer, nullable=True, comment="환산임대료평균")
    LET_CASCNT = Column(Integer, nullable=True, comment="임대건수")

class Facilities(Base):
    __tablename__ = "facilities"

    facility_id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)    
    quarter = Column(Integer, nullable=False)  
    region_name = Column(String(100), index=True, nullable=False) 

    viatr_fclty_co = Column(Integer, nullable=True)     
    pblofc_co = Column(Integer, nullable=True)          
    bank_co = Column(Integer, nullable=True)        
    gehspt_co = Column(Integer, nullable=True)         
    gnrl_hsptl_co = Column(Integer, nullable=True)   
    parmacy_co = Column(Integer, nullable=True)         
    kndrgr_co = Column(Integer, nullable=True)        
    elesch_co = Column(Integer, nullable=True)          
    mskul_co = Column(Integer, nullable=True)           
    hgschl_co = Column(Integer, nullable=True)           
    univ_co = Column(Integer, nullable=True)             
    drts_co = Column(Integer, nullable=True)            
    supmk_co = Column(Integer, nullable=True)           
    theat_co = Column(Integer, nullable=True)            
    stayng_fclty_co = Column(Integer, nullable=True)
    arprt_co = Column(Integer, nullable=True)          
    rlroad_statn_co = Column(Integer, nullable=True)   
    bus_trminl_co = Column(Integer, nullable=True)      
    subway_statn_co = Column(Integer, nullable=True)    
    bus_sttn_co = Column(Integer, nullable=True)        

    created_at = Column(DateTime, default=datetime.datetime.now, comment="데이터 수집 시점")

