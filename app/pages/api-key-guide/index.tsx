import React from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Stack,
  Button,
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Alert,
  Chip,
  Divider
} from '@mui/material';
import { useRouter } from 'next/router';
import {
  OpenInNew as OpenInNewIcon,
  ArrowBack as ArrowBackIcon,
  Key as KeyIcon,
  AccountCircle as AccountCircleIcon,
  CreditCard as CreditCardIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  Info as InfoIcon
} from '@mui/icons-material';

const ApiKeyGuidePage: React.FC = () => {
  const router = useRouter();

  const steps = [
    {
      label: 'OpenAI 계정 생성',
      content: (
        <Box>
          <Typography variant="body1" sx={{ mb: 2 }}>
            먼저 OpenAI 공식 웹사이트에서 계정을 생성해야 합니다.
          </Typography>
          <Button
            variant="outlined"
            startIcon={<OpenInNewIcon />}
            onClick={() => window.open('https://platform.openai.com/signup', '_blank')}
            sx={{ mb: 2 }}
          >
            OpenAI 회원가입 페이지로 이동
          </Button>
          <Typography variant="body2" color="text.secondary">
            • 이메일 주소와 비밀번호로 간단하게 가입할 수 있습니다<br/>
            • Google 계정으로도 가입 가능합니다
          </Typography>
        </Box>
      )
    },
    {
      label: '결제 정보 등록',
      content: (
        <Box>
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="body2">
              <strong>중요:</strong> API Key를 사용하려면 결제 정보를 등록해야 합니다.
            </Typography>
          </Alert>
          <Typography variant="body1" sx={{ mb: 2 }}>
            OpenAI API는 사용량에 따라 과금되는 서비스입니다.
          </Typography>
          <Stack spacing={1} sx={{ mb: 2 }}>
            <Typography variant="body2">• 신용카드 또는 직불카드 등록 필요</Typography>
            <Typography variant="body2">• 최소 $5 충전 권장</Typography>
            <Typography variant="body2">• 사용량 제한 설정 가능</Typography>
          </Stack>
          <Button
            variant="outlined"
            startIcon={<CreditCardIcon />}
            onClick={() => window.open('https://platform.openai.com/account/billing/overview', '_blank')}
          >
            결제 정보 설정하기
          </Button>
        </Box>
      )
    },
    {
      label: 'API Key 생성',
      content: (
        <Box>
          <Typography variant="body1" sx={{ mb: 2 }}>
            API Keys 페이지에서 새로운 API Key를 생성합니다.
          </Typography>
          <Stack spacing={2} sx={{ mb: 2 }}>
            <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                1. API Keys 페이지 접속
              </Typography>
              <Button
                variant="contained"
                startIcon={<KeyIcon />}
                onClick={() => window.open('https://platform.openai.com/api-keys', '_blank')}
                sx={{ mb: 1 }}
              >
                API Keys 페이지로 이동
              </Button>
            </Box>
            <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                2. "Create new secret key" 클릭
              </Typography>
              <Typography variant="body2" color="text.secondary">
                페이지 상단의 녹색 버튼을 클릭합니다.
              </Typography>
            </Box>
            <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                3. API Key 이름 설정 (선택사항)
              </Typography>
              <Typography variant="body2" color="text.secondary">
                "CVPilot" 등 구분하기 쉬운 이름을 입력하세요.
              </Typography>
            </Box>
            <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                4. API Key 복사 및 저장
              </Typography>
              <Typography variant="body2" color="text.secondary">
                생성된 API Key를 안전한 곳에 복사해두세요. (한 번만 표시됩니다)
              </Typography>
            </Box>
          </Stack>
        </Box>
      )
    },
    {
      label: 'CVPilot에서 사용',
      content: (
        <Box>
          <Typography variant="body1" sx={{ mb: 2 }}>
            생성한 API Key를 CVPilot에 입력하여 모든 AI 기능을 사용하세요.
          </Typography>
          <Stack spacing={2}>
            <Alert severity="success">
              <Typography variant="body2">
                <strong>완료!</strong> 이제 CVPilot의 모든 AI 기능을 자유롭게 사용할 수 있습니다.
              </Typography>
            </Alert>
            <Button
              variant="contained"
              onClick={() => router.push('/')}
              sx={{ alignSelf: 'flex-start' }}
            >
              메인 페이지로 돌아가기
            </Button>
          </Stack>
        </Box>
      )
    }
  ];

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      bgcolor: 'grey.50',
      transform: 'scale(0.8)',
      transformOrigin: 'top center',
      width: '125%',
      marginLeft: '-12.5%'
    }}>
      {/* 헤더 */}
      <Box sx={{ 
        bgcolor: 'white', 
        borderBottom: '1px solid',
        borderColor: 'divider',
        py: 2
      }}>
        <Container maxWidth="lg">
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={() => router.back()}
              sx={{ color: 'text.secondary' }}
            >
              돌아가기
            </Button>
            <Typography variant="h5" sx={{ fontWeight: 600 }}>
              OpenAI API Key 발급 가이드
            </Typography>
          </Box>
        </Container>
      </Box>

      <Container maxWidth="md" sx={{ py: 4 }}>
        {/* 소개 섹션 */}
        <Paper sx={{ p: 4, mb: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <KeyIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 2 }}>
              OpenAI API Key 발급 방법
            </Typography>
            <Typography variant="body1" color="text.secondary">
              CVPilot의 모든 AI 기능을 사용하기 위해 필요한 OpenAI API Key를 발급받는 방법을 안내합니다.
            </Typography>
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* 중요 정보 */}
          <Stack spacing={2} sx={{ mb: 3 }}>
            <Alert severity="info" icon={<InfoIcon />}>
              <Typography variant="body2">
                <strong>API Key란?</strong> OpenAI의 AI 서비스를 사용하기 위한 인증 키입니다. 
                이 키를 통해 GPT-4 등의 AI 모델을 사용할 수 있습니다.
              </Typography>
            </Alert>
            
            <Alert severity="warning" icon={<WarningIcon />}>
              <Typography variant="body2">
                <strong>비용 안내:</strong> OpenAI API는 사용량에 따라 과금됩니다. 
                일반적인 CV 분석 1회당 약 $0.01-0.05 정도의 비용이 발생합니다.
              </Typography>
            </Alert>

            <Alert severity="error" icon={<SecurityIcon />}>
              <Typography variant="body2">
                <strong>보안 주의:</strong> API Key는 절대 다른 사람과 공유하지 마세요. 
                CVPilot은 API Key를 서버에 저장하지 않고 브라우저에만 보관합니다.
              </Typography>
            </Alert>
          </Stack>
        </Paper>

        {/* 단계별 가이드 */}
        <Paper sx={{ p: 4 }}>
          <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
            단계별 발급 방법
          </Typography>
          
          <Stepper orientation="vertical">
            {steps.map((step, index) => (
              <Step key={index} active={true} completed={false}>
                <StepLabel>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {step.label}
                  </Typography>
                </StepLabel>
                <StepContent>
                  <Box sx={{ pb: 2 }}>
                    {step.content}
                  </Box>
                </StepContent>
              </Step>
            ))}
          </Stepper>
        </Paper>

        {/* 추가 정보 */}
        <Paper sx={{ p: 4, mt: 4 }}>
          <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
            자주 묻는 질문
          </Typography>
          
          <Stack spacing={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                  Q. API Key 사용 비용이 얼마나 되나요?
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  A. CVPilot 사용 시 일반적으로 CV 분석 1회당 $0.01-0.05, 트렌드 분석 1회당 $0.02-0.10 정도입니다. 
                  정확한 비용은 OpenAI 사용량 페이지에서 확인할 수 있습니다.
                </Typography>
              </CardContent>
            </Card>

            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                  Q. API Key가 안전한가요?
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  A. CVPilot은 API Key를 서버에 저장하지 않고 브라우저의 로컬 스토리지에만 보관합니다. 
                  하지만 공용 컴퓨터 사용 시에는 주의하시고, 필요시 OpenAI에서 API Key를 삭제할 수 있습니다.
                </Typography>
              </CardContent>
            </Card>

            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                  Q. 무료로 사용할 수 있나요?
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  A. OpenAI는 신규 가입자에게 일정 크레딧을 제공하지만, 지속적인 사용을 위해서는 결제 정보 등록이 필요합니다. 
                  사용량 제한을 설정하여 예상치 못한 과금을 방지할 수 있습니다.
                </Typography>
              </CardContent>
            </Card>
          </Stack>
        </Paper>

        {/* 빠른 링크 */}
        <Paper sx={{ p: 4, mt: 4, textAlign: 'center' }}>
          <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
            빠른 링크
          </Typography>
          
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center">
            <Button
              variant="contained"
              startIcon={<OpenInNewIcon />}
              onClick={() => window.open('https://platform.openai.com/api-keys', '_blank')}
              size="large"
            >
              OpenAI API Keys 페이지
            </Button>
            <Button
              variant="outlined"
              startIcon={<CreditCardIcon />}
              onClick={() => window.open('https://platform.openai.com/account/billing/overview', '_blank')}
              size="large"
            >
              결제 정보 설정
            </Button>
            <Button
              variant="outlined"
              onClick={() => router.push('/')}
              size="large"
            >
              CVPilot 메인으로
            </Button>
          </Stack>
        </Paper>
      </Container>
    </Box>
  );
};

export default ApiKeyGuidePage; 