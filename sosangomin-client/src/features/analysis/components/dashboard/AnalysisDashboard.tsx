// src/features/analysis/components/dashboard/AnalysisDashboard.tsx
import React, { useState, useEffect, useCallback } from "react";
import { useParams } from "react-router-dom";
import StatsCard from "./StatsCard";
import SummarySection from "./SummarySection";
import HourlySalesSection from "./HourlySalesSection";
import TopProductsSection from "./TopProductsSection";
import WeekdaySalesSection from "./WeekdaySalesSection";
import DistributionSection from "./DistributionSection";
import SeasonalSalesSection from "./SeasonalSalesSection";
import AnalysisSelector from "./AnalysisSelector";
import Loading from "@/components/common/Loading";
import useAnalysisStore from "@/store/useAnalysisStore";
import useStoreStore from "@/store/storeStore";
import WeatherSalesSection from "./WeatherSalesSection";
import TemperatureSalesSection from "./TemperatureSalesSection";
import PredictedSalesSection from "./PredictedSalesSection";
import ProductClusterSection from "./ProductClusterSection";
import DateRangeSection from "./DateRangeSection";
import ProductShareSection from "./ProductShareSection";
import { getAnalysisResult } from "../../api/analysisApi";
import MonthlySalesSection from "./MonthlySalesSection";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

const AnalysisDashboard: React.FC = () => {
  const { analysisId } = useParams<{ analysisId?: string }>();
  const [isExporting, setIsExporting] = React.useState(false);

  // Zustand에서 대표 매장 정보 가져오기
  const { representativeStore } = useStoreStore();

  // 스토어에서 상태와 액션 가져오기
  const {
    currentAnalysis,
    analysisList,
    isLoading,
    isLoadingList,
    error,
    listError,
    fetchStoreAnalysisList,
    fetchAnalysisResult,
    selectedAnalysisId: storeSelectedAnalysisId,
    setSelectedAnalysisId,
    debugState
  } = useAnalysisStore();

  const handleExportPDF = async () => {
    const reportElement = document.getElementById("research-page");
    if (!reportElement) return;

    setIsExporting(true); // 시작할 때 로딩
    reportElement.classList.add("pdf-export");

    try {
      const canvas = await html2canvas(reportElement, {
        scale: 2,
        useCORS: true
      });

      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF("p", "mm", "a4");
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();

      const imgProps = pdf.getImageProperties(imgData);
      const imgWidth = pageWidth;
      const imgHeight = (imgProps.height * imgWidth) / imgProps.width;

      if (imgHeight <= pageHeight) {
        pdf.addImage(imgData, "PNG", 0, 0, imgWidth, imgHeight);
      } else {
        const canvasHeight = canvas.height;
        const canvasWidth = canvas.width;
        const pageCanvas = document.createElement("canvas");
        const pageContext = pageCanvas.getContext("2d")!;
        const pageHeightPx = (pageHeight * canvasWidth) / pageWidth;

        let renderedHeight = 0;

        while (renderedHeight < canvasHeight) {
          pageCanvas.width = canvasWidth;
          pageCanvas.height = Math.min(
            pageHeightPx,
            canvasHeight - renderedHeight
          );
          pageContext.clearRect(0, 0, canvasWidth, pageCanvas.height);
          pageContext.drawImage(
            canvas,
            0,
            renderedHeight,
            canvasWidth,
            pageCanvas.height,
            0,
            0,
            canvasWidth,
            pageCanvas.height
          );
          const pageData = pageCanvas.toDataURL("image/png");
          if (renderedHeight > 0) pdf.addPage();
          pdf.addImage(
            pageData,
            "PNG",
            0,
            0,
            imgWidth,
            (pageCanvas.height * imgWidth) / canvasWidth
          );
          renderedHeight += pageHeightPx;
        }
      }

      pdf.save(`데이터 분석 보고서.pdf`);
    } catch (error) {
      console.error("PDF export error:", error);
    } finally {
      setIsExporting(false); // 끝나면 로딩 종료
      reportElement.classList.remove("pdf-export");
    }
  };

  // 원본 API 데이터를 저장하기 위한 상태
  const [originalApiData, setOriginalApiData] = useState<any>(null);
  const [loadingApiData, setLoadingApiData] = useState<boolean>(false);

  // 현재 선택된 분석 ID 상태 - URL 파라미터, 스토어 값, 로컬 상태 중 우선순위가 높은 값 사용
  const [localSelectedAnalysisId, setLocalSelectedAnalysisId] = useState<
    string | undefined
  >(analysisId || storeSelectedAnalysisId || undefined);

  // 변환된 분석 목록 및 선택된 분석 항목 상태
  const [displayAnalysisList, setDisplayAnalysisList] = useState<any[]>([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState<any | null>(null);

  // 마운트 시 상태 로깅
  useEffect(() => {
    if (debugState) {
      debugState();
    }
  }, [
    storeSelectedAnalysisId,
    analysisId,
    localSelectedAnalysisId,
    debugState
  ]);

  // 직접 API 호출을 통해 원본 데이터 가져오기
  useEffect(() => {
    if (localSelectedAnalysisId) {
      setLoadingApiData(true);
      getAnalysisResult(localSelectedAnalysisId)
        .then((response) => {
          setOriginalApiData(response);
          setLoadingApiData(false);
        })
        .catch((err) => {
          console.error("직접 API 호출 오류:", err);
          setLoadingApiData(false);
        });
    }
  }, [localSelectedAnalysisId]);

  // URL 또는 스토어의 선택된 분석 ID가 변경되면 로컬 상태 업데이트
  useEffect(() => {
    // 우선순위: URL 파라미터 > 스토어 값 > 기존 로컬 값
    const newSelectedId =
      analysisId || storeSelectedAnalysisId || localSelectedAnalysisId;

    if (newSelectedId && newSelectedId !== localSelectedAnalysisId) {
      setLocalSelectedAnalysisId(newSelectedId);

      // 스토어의 selectedAnalysisId도 동기화
      if (newSelectedId !== storeSelectedAnalysisId) {
        setSelectedAnalysisId(newSelectedId);
      }

      // 분석 결과가 없으면 해당 분석 결과 로드
      if (!currentAnalysis) {
        fetchAnalysisResult(newSelectedId).catch((err) => {
          console.error("분석 결과 로드 오류:", err);
        });
      }
    }
  }, [
    storeSelectedAnalysisId,
    analysisId,
    localSelectedAnalysisId,
    currentAnalysis,
    setSelectedAnalysisId,
    fetchAnalysisResult
  ]);

  // 분석 목록 로드
  useEffect(() => {
    if (!representativeStore?.store_id) return;

    const loadAnalysisList = async () => {
      // result 변수를 제거하고 직접 함수 호출
      await fetchStoreAnalysisList(representativeStore.store_id);

      if (debugState) {
        debugState();
      }
    };

    loadAnalysisList();
  }, [representativeStore, fetchStoreAnalysisList, debugState]);

  // 분석 목록이 로드되면, 목록을 컴포넌트가 이해할 수 있는 형식으로 변환
  useEffect(() => {
    if (analysisList && (analysisList.analysisList || analysisList.analyses)) {
      const list = analysisList.analysisList || analysisList.analyses;
      const convertedList = list.map((item: any) => ({
        analysis_id: item.analysisId || item.analysis_id,
        created_at: item.createdAt || item.created_at,
        store_id: representativeStore?.store_id,
        status: "success" // API에서 상태 정보가 없으면 success로 가정
      }));

      setDisplayAnalysisList(convertedList);

      // 선택된 분석 ID가 없으면 첫 번째 항목 선택
      if (!localSelectedAnalysisId && convertedList.length > 0) {
        const firstAnalysisId = convertedList[0].analysis_id;

        setLocalSelectedAnalysisId(firstAnalysisId);
        setSelectedAnalysisId(firstAnalysisId); // 스토어에도 설정
        setSelectedAnalysis(convertedList[0]);
        fetchAnalysisResult(firstAnalysisId);
      } else if (localSelectedAnalysisId) {
        // 선택된 분석이 있으면 해당 분석 정보 설정
        const selected = convertedList.find(
          (item: any) => item.analysis_id === localSelectedAnalysisId
        );
        if (selected) {
          setSelectedAnalysis(selected);
          fetchAnalysisResult(localSelectedAnalysisId);
        } else {
          console.warn(
            `선택된 분석 ID ${localSelectedAnalysisId}를 목록에서 찾을 수 없음`
          );
        }
      }
    }
  }, [
    analysisList,
    localSelectedAnalysisId,
    fetchAnalysisResult,
    representativeStore,
    setSelectedAnalysisId
  ]);

  useEffect(() => {
    // 데이터 로딩이 끝났는데도 currentAnalysis가 없는 경우
    if (!isLoading && !currentAnalysis && localSelectedAnalysisId) {
      fetchAnalysisResult(localSelectedAnalysisId).catch((err) => {
        console.error("재시도 분석 결과 로드 오류:", err);
      });
    }
  }, [
    analysisList,
    currentAnalysis,
    localSelectedAnalysisId,
    isLoading,
    fetchAnalysisResult
  ]);

  // 분석 선택 핸들러
  const handleAnalysisSelect = useCallback(
    (analysisId: string) => {
      // 로컬 상태 업데이트
      setLocalSelectedAnalysisId(analysisId);

      // Zustand 스토어 상태 업데이트
      setSelectedAnalysisId(analysisId);

      // 선택된 분석 항목 설정
      const selected = displayAnalysisList.find(
        (item) => item.analysis_id === analysisId
      );
      if (selected) {
        setSelectedAnalysis(selected);
      } else {
        console.warn(`선택한 분석 ID ${analysisId}를 목록에서 찾을 수 없음`);
      }

      // 분석 결과 가져오기
      fetchAnalysisResult(analysisId).catch((err) => {
        console.error("분석 결과 로드 오류:", err);
      });
    },
    [displayAnalysisList, fetchAnalysisResult, setSelectedAnalysisId]
  );

  // 통합 로딩 상태
  const isLoadingData = isLoading || isLoadingList || loadingApiData;
  const anyError = error || listError;

  // 대표 매장이 없는 경우 로딩 화면 표시
  if (!representativeStore) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-basic-white rounded-lg shadow-2xl p-8 max-w-md text-center border border-gray-200">
          <svg
            className="w-16 h-16 text-bit-main mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h2 className="text-2xl font-semibold text-bit-main mb-4">
            등록된 매장이 없습니다
          </h2>
          <p className="text-comment mb-6">
            분석 보고서를 생성하기 위해서는 매장 등록이 필요합니다.
          </p>
          <a
            href="/mypage" // 매장 등록 페이지 경로로 수정
            className="inline-block py-3 px-6 bg-bit-main text-basic-white rounded-md hover:bg-opacity-90 transition duration-200"
          >
            매장 등록하기
          </a>
        </div>
      </div>
    );
  }
  if (isLoadingData) return <Loading />;
  if (anyError)
    return (
      <div className="bg-basic-white rounded-lg shadow-[0_0_15px_rgba(0,0,0,0.1)] p-6 mb-6 min-h-[300px]">
        <div className="flex flex-col items-center justify-center h-full">
          <svg
            className="w-16 h-16 text-red-500 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <h2 className="text-xl font-semibold text-center text-bit-main mb-2">
            오류가 발생했습니다
          </h2>
          <p className="text-comment text-center mb-4">
            데이터를 불러오는데 오류가 발생 되었습니다.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="py-2 px-4 bg-bit-main hover:bg-opacity-90 text-basic-white rounded-md transition duration-200"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  if (!currentAnalysis && !originalApiData) {
    return (
      <div className="bg-basic-white rounded-lg shadow-[0_0_15px_rgba(0,0,0,0.1)] p-6 mb-6 min-h-[300px]">
        <div className="flex flex-col mt-20 items-center justify-center h-full">
          <h2 className="text-xl font-semibold text-bit-main mb-4">
            분석된 보고서가 없습니다
          </h2>
          <p className="text-comment text-center mb-4">
            {representativeStore.store_name}의 분석 보고서가 아직 없습니다.
          </p>
        </div>
      </div>
    );
  }

  // 직접 호출한 API 데이터가 있으면 그것을 사용하고, 없으면 currentAnalysis 사용
  let resultData, autoAnalysisResults, summary;

  if (originalApiData && originalApiData.analysis_result) {
    // 직접 API 호출로 가져온 데이터 사용
    const analysisResult = originalApiData.analysis_result;
    resultData = analysisResult.eda_result?.result_data || {};
    autoAnalysisResults = analysisResult.auto_analysis_results || {};
    summary = analysisResult.eda_result?.summary || "";
  } else {
    // currentAnalysis 사용 (이미 변환된 형태)
    resultData = currentAnalysis.result_data || {};
    autoAnalysisResults = currentAnalysis.auto_analysis_results || {};
    summary = currentAnalysis.summary || "";
  }

  // 컴포넌트에 전달할 데이터 구조화
  const data = {
    result_data: resultData,
    summary: summary,
    analysis_id:
      currentAnalysis?._id || originalApiData?.analysis_result?._id || "",
    created_at:
      currentAnalysis?.created_at ||
      originalApiData?.analysis_result?.created_at ||
      "",
    status:
      currentAnalysis?.status || originalApiData?.analysis_result?.status || "",
    data_range:
      currentAnalysis?.data_range ||
      originalApiData?.analysis_result?.data_range ||
      undefined,
    auto_analysis_results: autoAnalysisResults
  };

  // 기본 통계 데이터
  const basicStats = resultData?.basic_stats?.data || {
    total_sales: 0,
    avg_transaction: 0,
    total_transactions: 0,
    unique_products: 0,
    customer_avg: 0
  };

  // 전체 요약
  const overallSummary = summary;

  return (
    <div>
      <div className="max-w-[1200px] mx-auto p-6">
        <div className="flex flex-col lg:flex-row justify-between items-start sm:items-center mb-15 gap-4">
          <h1 className="text-xl font-bold text-comment">
            <span className="text-bit-main font-bold text-2xl">
              {representativeStore.store_name}
            </span>{" "}
            매장 분석
          </h1>

          {/* 분석 선택기 - API에서 로드된 분석 목록 전달 */}
          <div className="flex items-center">
            <AnalysisSelector
              storeId={representativeStore.store_id}
              analysisList={displayAnalysisList}
              currentAnalysisId={localSelectedAnalysisId}
              selectedAnalysis={selectedAnalysis}
              onAnalysisSelect={handleAnalysisSelect}
            />
            <button
              onClick={handleExportPDF}
              className="ml-5 px-3 py-2 bg-bit-main hover:bg-blue-900 text-white rounded-lg text-sm transition"
            >
              PDF 추출
            </button>
          </div>
        </div>

        <DateRangeSection dataRange={data.data_range} />

        {/* 전체 요약 섹션 */}
        <SummarySection summary={overallSummary} />

        {/* 기본 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-6">
          <StatsCard title="총 매출" value={basicStats.total_sales} />
          <StatsCard
            title="평균 거래 금액"
            value={`₩${Math.round(basicStats.avg_transaction).toLocaleString(
              "ko-KR"
            )}`}
          />
          <StatsCard
            title="총 거래 건수"
            value={`${basicStats.total_transactions}건`}
          />
        </div>

        {/* 예측 매출 섹션 */}
        {originalApiData?.analysis_result && (
          <PredictedSalesSection
            data={{
              ...data,
              auto_analysis_results:
                originalApiData.analysis_result.auto_analysis_results
            }}
          />
        )}
        {/* 인기 메뉴 랭킹 섹션 */}
        <TopProductsSection data={data} />

        {/* 제품 점유율 섹션 */}
        <ProductShareSection data={data} />

        {/* 상품 클러스터 분석 섹션 */}
        {originalApiData?.analysis_result && (
          <ProductClusterSection
            data={{
              ...data,
              auto_analysis_results:
                originalApiData.analysis_result.auto_analysis_results
            }}
          />
        )}

        {/* 평일/휴일 매출 비율 & 시간대별 매출 분석 섹션 */}
        <DistributionSection data={data} />

        {/* 월별 매출 섹션 */}
        <MonthlySalesSection data={data} />

        {/* 요일별 매출 현황 섹션 */}
        <WeekdaySalesSection data={data} />

        {/* 시간별 매출 섹션 */}
        <HourlySalesSection data={data} />

        {/* 기온별 매출 섹션 */}
        <TemperatureSalesSection data={data} />

        {/* 날씨별 매출 섹션 */}
        <WeatherSalesSection data={data} />

        {/* 계절별 매출 섹션 */}
        <SeasonalSalesSection data={data} />
      </div>
      {isExporting && (
        <div className="fixed inset-0 bg-white bg-opacity-80 z-50 flex justify-center items-center">
          <Loading />
        </div>
      )}
    </div>
  );
};

export default AnalysisDashboard;
