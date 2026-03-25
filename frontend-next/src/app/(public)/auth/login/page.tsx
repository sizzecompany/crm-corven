'use client';
import { useState } from 'react';
import { authService } from '@/services/auth.service';
import { PageShell } from '@/components/layout/page-shell';
export default function Page(){const [email,setEmail]=useState(''); const [msg,setMsg]=useState(''); return <PageShell title='Login (OTP)' description='POST /api/v1/auth/request-otp'><form className='space-y-3 max-w-md' onSubmit={async(e)=>{e.preventDefault();const r=await authService.requestOtp(email);setMsg(r.data.message ?? 'OTP solicitado');}}><input value={email} onChange={(e)=>setEmail(e.target.value)} placeholder='email' /><button className='bg-primary px-3 py-2'>Solicitar OTP</button></form><p>{msg}</p></PageShell>}
