'use client';

import { FormEvent, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { authApi } from '@/services/auth';

type Step = 'email' | 'otp' | 'success';

function getErrorMessage(error: unknown) {
  const fallback = 'Não foi possível concluir a operação. Tente novamente.';
  if (typeof error !== 'object' || error === null) return fallback;

  const response = (error as { response?: { status?: number; data?: { detail?: string } } }).response;
  if (!response) return fallback;

  if (response.status === 400) return 'E-mail inválido ou payload incorreto.';
  if (response.status === 401) return 'OTP inválido ou expirado.';
  if (response.status === 404) return 'Usuário não encontrado para este e-mail.';
  if (response.status === 429) return 'Muitas tentativas. Aguarde e tente novamente.';
  return response.data?.detail ?? fallback;
}

export default function LoginPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>('email');
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const isEmailStep = step === 'email';
  const isOtpStep = step === 'otp';

  const ctaLabel = useMemo(() => {
    if (isLoading) return 'Processando...';
    if (isEmailStep) return 'Enviar código OTP';
    return 'Validar OTP e entrar';
  }, [isLoading, isEmailStep]);

  const handleRequestOtp = async (event: FormEvent) => {
    event.preventDefault();
    setErrorMessage('');
    setStatusMessage('');
    setIsLoading(true);

    try {
      const { data } = await authApi.requestOtp({ email });
      setStatusMessage(data.otp_code_dev_only ? `${data.message} Código dev: ${data.otp_code_dev_only}` : data.message);
      setStep('otp');
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOtp = async (event: FormEvent) => {
    event.preventDefault();
    setErrorMessage('');
    setStatusMessage('');
    setIsLoading(true);

    try {
      const { data } = await authApi.verifyOtp({ email, code });
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      document.cookie = `access_token=${data.access_token}; path=/`;

      setStep('success');
      setStatusMessage('OTP validado com sucesso. Redirecionando...');
      router.push('/dashboard');
      router.refresh();
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-b from-[#0f172a] via-[#111833] to-[#1f2a4d] p-4 text-foreground">
      <section className="w-full max-w-md rounded-2xl border border-border bg-card/80 p-6 shadow-xl backdrop-blur">
        <h1 className="mb-1 text-2xl font-semibold">Acessar CRM Corven</h1>
        <p className="mb-6 text-sm text-muted">Login passwordless via OTP por e-mail.</p>

        <form className="space-y-4" onSubmit={isEmailStep ? handleRequestOtp : handleVerifyOtp}>
          <div className="space-y-2">
            <label className="text-sm">E-mail</label>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="voce@empresa.com"
              required
              disabled={isLoading || step === 'success' || isOtpStep}
              className="w-full"
            />
          </div>

          {isOtpStep ? (
            <div className="space-y-2">
              <label className="text-sm">Código OTP (6 dígitos)</label>
              <input
                type="text"
                value={code}
                onChange={(event) => setCode(event.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="000000"
                required
                maxLength={6}
                className="w-full tracking-[0.35em]"
              />
            </div>
          ) : null}

          <button
            type="submit"
            disabled={isLoading || step === 'success'}
            className="flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-2 font-medium text-primary-foreground disabled:opacity-60"
          >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            {ctaLabel}
          </button>

          {isOtpStep ? (
            <button
              type="button"
              disabled={isLoading}
              className="w-full rounded-md border border-border px-4 py-2 text-sm"
              onClick={async () => {
                setErrorMessage('');
                setIsLoading(true);
                try {
                  const { data } = await authApi.requestOtp({ email });
                  setStatusMessage(data.message);
                } catch (error) {
                  setErrorMessage(getErrorMessage(error));
                } finally {
                  setIsLoading(false);
                }
              }}
            >
              Reenviar código
            </button>
          ) : null}
        </form>

        {statusMessage ? <p className="mt-4 rounded-md border border-primary/40 bg-primary/10 p-3 text-sm">{statusMessage}</p> : null}
        {errorMessage ? <p className="mt-4 rounded-md border border-danger/40 bg-danger/10 p-3 text-sm text-danger">{errorMessage}</p> : null}
      </section>
    </main>
  );
}
