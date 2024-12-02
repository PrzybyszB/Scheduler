import { useRouter } from "next/router";

const useHandleButtonClick = () => {
  const router = useRouter();

  return (id: string) => {
    router.push(`/route/${id}`);
  };
};

export default useHandleButtonClick;