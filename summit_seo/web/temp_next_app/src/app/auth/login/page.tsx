'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/providers/auth-provider';
import { Button } from '@/components/ui/button';
import { Container } from '@/components/ui/container';
import { Section } from '@/components/ui/section';
import { AnimatedContainer } from '@/components/ui/animated-container';
import { motion } from 'framer-motion';
import { useReducedMotion } from '@/lib/motion';
import { authPageTransition } from '@/lib/motion';
import {
  AnimatedInput,
  AnimatedFormField,
  AnimatedLabel,
  AnimatedError,
  AnimatedSuccess,
  AnimatedButtonWrapper,
  LoadingSpinner,
  FormSection
} from '@/components/ui/auth-animated-elements';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  const router = useRouter();
  const searchParams = useSearchParams();
  const { signIn, user } = useAuth();
  const prefersReducedMotion = useReducedMotion();
  
  // Handle redirect parameters
  const redirect = searchParams.get('redirect');
  const registeredParam = searchParams.get('registered');
  const resetParam = searchParams.get('reset');

  // Set appropriate messages based on URL parameters
  useEffect(() => {
    if (registeredParam === 'true') {
      setSuccessMessage('Account created successfully! Please sign in.');
    } else if (resetParam === 'success') {
      setSuccessMessage('Password reset successfully! Please sign in with your new password.');
    }
  }, [registeredParam, resetParam]);
  
  // Redirect to dashboard or specified redirect path if already logged in
  useEffect(() => {
    if (user) {
      if (redirect) {
        router.push(decodeURIComponent(redirect));
      } else {
        router.push('/dashboard');
      }
    }
  }, [user, router, redirect]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const { error: signInError } = await signIn(email, password);
      
      if (signInError) {
        setError(signInError.message || 'Failed to sign in');
        return;
      }
      
      // Redirect handled by useEffect when user state updates
    } catch (err) {
      setError('An unexpected error occurred');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      className="w-full"
      initial="initial"
      animate="animate"
      exit="exit"
      variants={authPageTransition}
    >
      <Section className="py-12">
        <Container className="max-w-md">
          <AnimatedContainer 
            variant="fadeIn" 
            className="bg-card p-8 rounded-lg shadow-sm"
            delay={0.1}
          >
            <AnimatedContainer variant="slideUp" delay={0.2}>
              <motion.h1 
                className="text-3xl font-bold mb-6 text-center"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ 
                  type: "spring",
                  stiffness: 500,
                  damping: 30,
                  delay: 0.2
                }}
              >
                Log In
              </motion.h1>
            </AnimatedContainer>
            
            <AnimatedSuccess message={successMessage} className="mb-6" />
            <AnimatedError message={error} className="mb-6" />
            
            <FormSection>
              <form onSubmit={handleSubmit} className="space-y-5">
                <AnimatedFormField delay={0.3}>
                  <AnimatedLabel htmlFor="email">
                    Email address
                  </AnimatedLabel>
                  <AnimatedInput
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    required
                  />
                </AnimatedFormField>
                
                <AnimatedFormField delay={0.4}>
                  <div className="flex justify-between">
                    <AnimatedLabel htmlFor="password">
                      Password
                    </AnimatedLabel>
                    <motion.div
                      whileHover={{ 
                        scale: prefersReducedMotion ? 1 : 1.05,
                        color: "rgb(var(--primary))"
                      }}
                    >
                      <Link href="/auth/forgot-password" className="text-sm hover:underline">
                        Forgot password?
                      </Link>
                    </motion.div>
                  </div>
                  <AnimatedInput
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    required
                  />
                </AnimatedFormField>
                
                <AnimatedFormField delay={0.5}>
                  <AnimatedButtonWrapper>
                    <Button 
                      type="submit" 
                      className="w-full" 
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <div className="flex items-center justify-center">
                          <LoadingSpinner />
                          <span className="ml-2">Signing in...</span>
                        </div>
                      ) : 'Sign in'}
                    </Button>
                  </AnimatedButtonWrapper>
                </AnimatedFormField>
              </form>
            </FormSection>
            
            <AnimatedContainer variant="fadeIn" delay={0.6}>
              <div className="mt-6 text-center">
                <motion.p 
                  className="text-sm"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.7 }}
                >
                  Don&apos;t have an account?{' '}
                  <motion.span
                    whileHover={{ 
                      scale: prefersReducedMotion ? 1 : 1.05,
                      color: "rgb(var(--primary))"
                    }}
                  >
                    <Link href="/auth/register" className="text-primary hover:underline">
                      Create an account
                    </Link>
                  </motion.span>
                </motion.p>
              </div>
            </AnimatedContainer>
          </AnimatedContainer>
        </Container>
      </Section>
    </motion.div>
  );
} 