import React, { useEffect, useState } from "react";
import { StoreListResponse, StoreInfo } from "@/features/auth/types/mypage";
import Store from "@/features/auth/components/mypage/Storeitem";
import useStoreStore from "@/store/storeStore";
import {
  getStoreList,
  postmainstore,
  deleteStore
} from "@/features/auth/api/mypageApi";

const StoreList: React.FC = () => {
  const [storeListData, setStoreListData] = useState<StoreListResponse | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(true);

  const { setRepresentativeStore } = useStoreStore();

  // 가게 목록 가져오기
  const fetchStores = async () => {
    setIsLoading(true);

    try {
      const response = await getStoreList();
      setStoreListData(response);

      // 대표 가게(is_main이 true인 가게) 찾기
      if (response.status === "success" && response.stores.length > 0) {
        const mainStore = response.stores.find(
          (store: StoreInfo) => store.is_main === true
        );
        if (mainStore) {
          setRepresentativeStore(mainStore);
        }
      }
    } catch (error) {
      console.error("가게 목록 불러오기 실패:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStores();
  }, [setRepresentativeStore]);

  // 대표 가게 설정 핸들러
  const handleSetRepresentative = async (store: StoreInfo) => {
    if (!store.store_id) {
      alert("가게 정보가 올바르지 않습니다.");
      return;
    }

    try {
      await postmainstore(store.store_id);
      await fetchStores();
      alert(`${store.store_name}이(가) 대표 가게로 설정되었습니다.`);
    } catch (error) {
      console.error("대표 가게 설정 실패:", error);
      alert("대표 가게 설정에 실패했습니다. 다시 시도해주세요.");
    }
  };

  // 가게 삭제 핸들러
  const handleDeleteStore = async (store: StoreInfo) => {
    if (!store.store_id) {
      alert("가게 정보가 올바르지 않습니다.");
      return;
    }

    try {
      await deleteStore(store.store_id);
      await fetchStores(); // 가게 목록 새로고침
      alert(`${store.store_name}이(가) 삭제되었습니다.`);
    } catch (error) {
      console.error("가게 삭제 실패:", error);
      alert("가게 삭제에 실패했습니다. 다시 시도해주세요.");
    }
  };

  if (isLoading) {
    return;
  }

  if (!storeListData || storeListData.stores.length === 0) {
    return (
      <div className="text-center py-8 bg-gray-50 rounded-lg">
        <p className="text-gray-500">
          {storeListData?.message || "등록된 가게가 없습니다."}
        </p>
      </div>
    );
  }

  return (
    <div className="">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {storeListData.stores.map((store) => (
          <Store
            key={store.store_id}
            store={store}
            isRepresentative={store.is_main}
            onSetRepresentative={handleSetRepresentative}
            onDeleteStore={handleDeleteStore}
          />
        ))}
      </div>
    </div>
  );
};

export default StoreList;
