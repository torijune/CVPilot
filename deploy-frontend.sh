#!/bin/bash

# AWS S3 + CloudFront 프론트엔드 배포 스크립트
set -e

# 설정
BUCKET_NAME="cvpilot-frontend"
REGION="us-east-1"
CLOUDFRONT_COMMENT="CVPilot Frontend Distribution"

echo "🚀 CVPilot 프론트엔드 S3 배포 시작..."

# 1. S3 버킷 생성 (존재하지 않으면)
echo "📦 S3 버킷 확인/생성 중..."
if ! aws s3api head-bucket --bucket $BUCKET_NAME 2>/dev/null; then
    echo "📦 S3 버킷 생성 중: $BUCKET_NAME"
    aws s3api create-bucket --bucket $BUCKET_NAME --region $REGION
    
    # 퍼블릭 액세스 차단 해제 (정적 웹사이트 호스팅용)
    aws s3api delete-public-access-block --bucket $BUCKET_NAME
    
    # 웹사이트 설정
    aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document 404.html
    
    # 버킷 정책 설정 (퍼블릭 읽기 허용)
    cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF
    aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json
    rm bucket-policy.json
else
    echo "✅ S3 버킷이 이미 존재합니다: $BUCKET_NAME"
fi

# 2. Next.js 빌드 (이미 빌드된 경우 스킵)
if [ ! -d "app/out" ]; then
  echo "🏗️ Next.js 빌드 중..."
  cd app
  npm run build
  cd ..
else
  echo "✅ 이미 빌드된 파일을 사용합니다."
fi

# 3. S3에 업로드
echo "📤 S3에 파일 업로드 중..."
aws s3 sync app/.next/static s3://$BUCKET_NAME/_next/static --delete

# 정적 사이트 파일들 업로드 (output: export 사용)
aws s3 sync app/out s3://$BUCKET_NAME --delete

# Next.js 정적 파일들도 업로드
if [ -d "app/public" ]; then
    aws s3 sync app/public s3://$BUCKET_NAME --delete
fi

# 4. CloudFront 배포 확인/생성
echo "🌐 CloudFront 배포 확인 중..."
DISTRIBUTION_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?Comment=='$CLOUDFRONT_COMMENT'].Id" --output text)

if [ -z "$DISTRIBUTION_ID" ] || [ "$DISTRIBUTION_ID" == "None" ]; then
    echo "🌐 CloudFront 배포 생성 중..."
    
    # CloudFront 배포 설정
    cat > cloudfront-config.json << EOF
{
    "CallerReference": "cvpilot-$(date +%s)",
    "Comment": "$CLOUDFRONT_COMMENT",
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-$BUCKET_NAME",
        "ViewerProtocolPolicy": "redirect-to-https",
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        },
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        }
    },
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-$BUCKET_NAME",
                "DomainName": "$BUCKET_NAME.s3.amazonaws.com",
                "S3OriginConfig": {
                    "OriginAccessIdentity": ""
                }
            }
        ]
    },
    "Enabled": true,
    "DefaultRootObject": "index.html"
}
EOF
    
    DISTRIBUTION_ID=$(aws cloudfront create-distribution --distribution-config file://cloudfront-config.json --query 'Distribution.Id' --output text)
    rm cloudfront-config.json
    
    echo "✅ CloudFront 배포 생성됨: $DISTRIBUTION_ID"
else
    echo "✅ CloudFront 배포가 이미 존재합니다: $DISTRIBUTION_ID"
fi

# 5. CloudFront 무효화 (캐시 갱신)
echo "🔄 CloudFront 캐시 무효화 중..."
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*" > /dev/null

# 6. URL 정보 출력
WEBSITE_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
CLOUDFRONT_URL=$(aws cloudfront get-distribution --id $DISTRIBUTION_ID --query 'Distribution.DomainName' --output text)

echo ""
echo "🎉 배포 완료!"
echo "📍 S3 Website URL: $WEBSITE_URL"
echo "🌐 CloudFront URL: https://$CLOUDFRONT_URL"
echo ""
echo "⚠️  CloudFront 배포는 전파에 10-15분 정도 소요될 수 있습니다."
echo "" 