// 예시: 파일 업로드 및 관심분야 전송
export async function uploadCVAndInterest(cvFile: File, interests: string[]) {
  const formData = new FormData();
  formData.append("cv", cvFile);
  formData.append("interests", JSON.stringify(interests));
  const res = await fetch("/api/v1/user/interest", {
    method: "POST",
    body: formData,
  });
  return res.json();
}

// 기타 단계별 API 함수도 여기에 추가
