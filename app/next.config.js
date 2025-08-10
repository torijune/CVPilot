/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // 정적 사이트 생성 설정
  output: 'export',
  trailingSlash: true,
  
  // 환경 변수 설정 (새 Lambda URL로 업데이트)
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'https://na6biybdk3xhs2lk337vtujjd40dbvcv.lambda-url.us-east-1.on.aws',
  },

  // 이미지 최적화 (정적 배포용)
  images: {
    unoptimized: true
  },

  // CORS 헤더 설정
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,OPTIONS,PATCH,DELETE,POST,PUT' },
          { key: 'Access-Control-Allow-Headers', value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version' },
        ],
      },
    ]
  },
}

module.exports = nextConfig 