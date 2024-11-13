import { useRouter } from "next/router";
import { Dispatch, SetStateAction } from "react";
import { StopData } from "../types";

const useHandleStopClick = (
  setNewSearch: Dispatch<SetStateAction<string>>,
  setStopId: (stop_id: string) => void
) => {
  const router = useRouter();

  const handleStopClick = (stop: StopData) => {
    setNewSearch("");
    setStopId(stop.stop_id);
    router.push(`stops/?stop_id=${stop.stop_id}`);
  };

  return handleStopClick;
};

export default useHandleStopClick;
