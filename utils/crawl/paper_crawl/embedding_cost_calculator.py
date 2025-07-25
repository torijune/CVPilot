#!/usr/bin/env python3
"""
OpenAI Embedding 비용 계산기
논문 제목과 초록을 text-embedding-3-small로 임베딩할 때의 비용을 계산합니다.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import tiktoken
from datetime import datetime

class EmbeddingCostCalculator:
    def __init__(self):
        # OpenAI text-embedding-3-small 모델 정보
        self.model_name = "text-embedding-3-small"
        self.cost_per_1k_tokens = 0.00002  # $0.00002 per 1K tokens (2024년 기준)
        
        # tiktoken 인코더 초기화
        try:
            self.encoder = tiktoken.encoding_for_model("gpt-4")  # text-embedding-3-small은 gpt-4와 같은 인코더 사용
        except:
            print("Warning: tiktoken not available, using character-based estimation")
            self.encoder = None
    
    def count_tokens(self, text: str) -> int:
        """텍스트의 정확한 토큰 수를 계산합니다."""
        if self.encoder:
            return len(self.encoder.encode(text))
        else:
            # 대략적인 추정 (영어 기준 1토큰 ≈ 4자)
            return len(text) // 4
    
    def calculate_embedding_cost(self, df: pd.DataFrame) -> Dict:
        """전체 데이터셋의 임베딩 비용을 계산합니다."""
        print("=== 임베딩 비용 계산 시작 ===")
        print(f"모델: {self.model_name}")
        print(f"비용: ${self.cost_per_1k_tokens:.5f} per 1K tokens")
        print()
        
        # 텍스트 길이 분석
        df['title_length'] = df['title'].str.len()
        df['abstract_length'] = df['abstract'].str.len()
        df['total_text_length'] = df['title_length'] + df['abstract_length']
        
        # 토큰 수 계산
        print("토큰 수 계산 중...")
        df['title_tokens'] = df['title'].apply(self.count_tokens)
        df['abstract_tokens'] = df['abstract'].apply(self.count_tokens)
        df['total_tokens'] = df['title_tokens'] + df['abstract_tokens']
        
        # 기본 통계
        total_papers = len(df)
        total_tokens = df['total_tokens'].sum()
        avg_tokens_per_paper = df['total_tokens'].mean()
        
        print(f"총 논문 수: {total_papers:,}개")
        print(f"총 토큰 수: {total_tokens:,}토큰")
        print(f"논문당 평균 토큰 수: {avg_tokens_per_paper:.1f}토큰")
        print()
        
        # 비용 계산
        cost_per_paper = (avg_tokens_per_paper / 1000) * self.cost_per_1k_tokens
        total_cost = (total_tokens / 1000) * self.cost_per_1k_tokens
        
        print("=== 비용 분석 ===")
        print(f"논문당 평균 비용: ${cost_per_paper:.6f}")
        print(f"전체 임베딩 비용: ${total_cost:.2f}")
        print(f"전체 임베딩 비용 (KRW): ₩{total_cost * 1300:.0f}")  # 1달러 = 1300원 가정
        print()
        
        # 학회별 분석
        print("=== 학회별 분석 ===")
        conference_stats = df.groupby('conference').agg({
            'total_tokens': ['count', 'sum', 'mean'],
            'title': 'count'
        }).round(2)
        
        conference_stats.columns = ['논문수', '총토큰수', '평균토큰수', '논문수2']
        conference_stats = conference_stats.drop('논문수2', axis=1)
        
        # 학회별 비용 계산
        conference_stats['예상비용'] = (conference_stats['총토큰수'] / 1000) * self.cost_per_1k_tokens
        conference_stats['예상비용_KRW'] = conference_stats['예상비용'] * 1300
        
        print(conference_stats)
        print()
        
        # Dense Retrieval 시나리오 분석
        print("=== Dense Retrieval 시나리오 ===")
        self.analyze_dense_retrieval_scenario(df)
        
        return {
            'total_papers': total_papers,
            'total_tokens': total_tokens,
            'avg_tokens_per_paper': avg_tokens_per_paper,
            'total_cost_usd': total_cost,
            'total_cost_krw': total_cost * 1300,
            'cost_per_paper': cost_per_paper,
            'conference_stats': conference_stats
        }
    
    def analyze_dense_retrieval_scenario(self, df: pd.DataFrame):
        """Dense Retrieval 사용 시나리오를 분석합니다."""
        print("시나리오 1: 전체 논문 임베딩 후 검색")
        print("  - 모든 논문을 한 번 임베딩하여 벡터 DB에 저장")
        print("  - 검색 시 쿼리만 임베딩하여 유사도 검색")
        print(f"  - 초기 설정 비용: ${(df['total_tokens'].sum() / 1000) * self.cost_per_1k_tokens:.2f}")
        print()
        
        print("시나리오 2: 학회별 선택적 임베딩")
        print("  - 각 학회에서 상위 3개 논문만 임베딩")
        
        # 각 학회별 상위 3개 논문 선택 (연도 기준)
        selected_papers = []
        for conference in df['conference'].unique():
            conf_papers = df[df['conference'] == conference].sort_values('year', ascending=False).head(3)
            selected_papers.append(conf_papers)
        
        selected_df = pd.concat(selected_papers, ignore_index=True)
        selected_tokens = selected_df['total_tokens'].sum()
        selected_cost = (selected_tokens / 1000) * self.cost_per_1k_tokens
        
        print(f"  - 선택된 논문 수: {len(selected_df)}개")
        print(f"  - 선택된 토큰 수: {selected_tokens:,}토큰")
        print(f"  - 선택적 임베딩 비용: ${selected_cost:.2f}")
        print(f"  - 선택적 임베딩 비용 (KRW): ₩{selected_cost * 1300:.0f}")
        print()
        
        print("시나리오 3: 실시간 임베딩")
        print("  - 검색할 때마다 쿼리와 관련 논문들을 실시간으로 임베딩")
        print("  - 캐싱 없이 매번 새로 계산")
        
        # 예상 검색 횟수와 비용
        estimated_searches_per_month = 100
        avg_query_length = 50  # 평균 쿼리 길이
        avg_retrieved_papers = 10  # 평균 검색 결과 수
        
        monthly_query_tokens = estimated_searches_per_month * self.count_tokens(" " * avg_query_length)
        monthly_paper_tokens = estimated_searches_per_month * avg_retrieved_papers * selected_df['total_tokens'].mean()
        monthly_total_tokens = monthly_query_tokens + monthly_paper_tokens
        monthly_cost = (monthly_total_tokens / 1000) * self.cost_per_1k_tokens
        
        print(f"  - 월 예상 검색 횟수: {estimated_searches_per_month}회")
        print(f"  - 월 예상 비용: ${monthly_cost:.2f}")
        print(f"  - 연 예상 비용: ${monthly_cost * 12:.2f}")
        print()
        
        # 권장사항
        print("=== 권장사항 ===")
        print("1. 초기 설정: 시나리오 2 (학회별 상위 3개 논문 임베딩)")
        print(f"   - 비용: ${selected_cost:.2f} (₩{selected_cost * 1300:.0f})")
        print("2. 검색 성능 향상 시: 시나리오 1 (전체 임베딩)")
        print(f"   - 비용: ${(df['total_tokens'].sum() / 1000) * self.cost_per_1k_tokens:.2f}")
        print("3. 실시간 검색: 시나리오 3 (필요시 실시간 임베딩)")
        print(f"   - 월 비용: ${monthly_cost:.2f}")

def main():
    """메인 실행 함수"""
    print("OpenAI Embedding 비용 계산기")
    print("=" * 50)
    
    # CSV 파일 읽기
    try:
        df = pd.read_csv('utils/crawl/paper_crawl/all_papers.csv')
        print(f"CSV 파일 로드 완료: {len(df):,}개 논문")
    except FileNotFoundError:
        print("Error: all_papers.csv 파일을 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f"Error: CSV 파일 읽기 실패 - {e}")
        return
    
    # 비용 계산기 초기화
    calculator = EmbeddingCostCalculator()
    
    # 비용 계산 실행
    results = calculator.calculate_embedding_cost(df)
    
    # 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results['conference_stats'].to_csv(f'embedding_cost_analysis_{timestamp}.csv')
    print(f"\n분석 결과가 'embedding_cost_analysis_{timestamp}.csv'에 저장되었습니다.")

if __name__ == "__main__":
    main() 