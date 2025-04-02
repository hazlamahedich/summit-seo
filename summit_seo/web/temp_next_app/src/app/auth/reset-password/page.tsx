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
  AnimatedButtonWrapper,
  LoadingSpinner,
  FormSection
} from '@/components/ui/auth-animated-elements';

export default function ResetPasswordPage() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tokenInvalid, setTokenInvalid] = useState(false);
  
  const router = useRouter();
  const searchParams = useSearchParams();
  const { updatePassword } = useAuth();
  const prefersReducedMotion = useReducedMotion();
  
  // Get token from URL
  const token = searchParams.get('token');
  
  // Check if token exists
  useEffect(() => {
    if (!token) {
      setTokenInvalid(true);
    }
  }, [token]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    
    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    // Check if token exists
    if (!token) {
      setTokenInvalid(true);
      return;
    }
    
    setIsLoading(true);

    try {
      const { error: resetError } = await updatePassword(password);
      
      if (resetError) {
        setError(resetError.message || 'Failed to reset password');
        return;
      }
      
      // Password reset successful, redirect to login with success message
      router.push('/auth/login?reset=success');
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
                Reset Password
              </motion.h1>
            </AnimatedContainer>
            
            {tokenInvalid ? (
              <AnimatedContainer variant="slideUp" delay={0.3}>
                <motion.div 
                  className="bg-destructive/15 text-destructive p-4 rounded-md mb-6"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ 
                    type: "spring",
                    stiffness: 500,
                    damping: 30,
                    duration: prefersReducedMotion ? 0.1 : 0.5
                  }}
                >
                  <p>Invalid or expired reset link. Please request a new password reset.</p>
                </motion.div>
                <AnimatedButtonWrapper>
                  <Button 
                    className="w-full" 
                    onClick={() => router.push('/auth/forgot-password')}
                  >
                    Request a new reset link
                  </Button>
                </AnimatedButtonWrapper>
              </AnimatedContainer>
            ) : (
              <>
                <AnimatedContainer variant="slideUp" delay={0.3}>
                  <motion.p 
                    className="text-muted-foreground mb-6 text-center"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                  >
                    Enter your new password below.
                  </motion.p>
                </AnimatedContainer>
                
                <AnimatedError message={error} className="mb-6" />
                
                <FormSection>
                  <form onSubmit={handleSubmit} className="space-y-5">
                    <AnimatedFormField delay={0.4}>
                      <AnimatedLabel htmlFor="password">
                        New Password
                      </AnimatedLabel>
                      <AnimatedInput
                        id="password"
                        type="password"
                        value={password}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                        placeholder="Enter your new password"
                        required
                      />
                    </AnimatedFormField>
                    
                    <AnimatedFormField delay={0.5}>
                      <AnimatedLabel htmlFor="confirmPassword">
                        Confirm New Password
                      </AnimatedLabel>
                      <AnimatedInput
                        id="confirmPassword"
                        type="password"
                        value={confirmPassword}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setConfirmPassword(e.target.value)}
                        placeholder="Confirm your new password"
                        required
                      />
                      <motion.div 
                        className="mt-2"
                        initial={{ opacity: 0 }}
                        animate={{ 
                          opacity: password && confirmPassword ? 1 : 0,
                          scale: password && confirmPassword ? 1 : 0.95
                        }}
                        transition={{ duration: 0.3 }}
                      >
                        {password && confirmPassword && (
                          <div className={`text-sm ${password === confirmPassword ? 'text-success' : 'text-destructive'}`}>
                            {password === confirmPassword ? '✓ Passwords match' : '✗ Passwords do not match'}
                          </div>
                        )}
                      </motion.div>
                    </AnimatedFormField>
                    
                    <AnimatedFormField delay={0.6}>
                      <AnimatedButtonWrapper>
                        <Button 
                          type="submit" 
                          className="w-full" 
                          disabled={isLoading}
                        >
                          {isLoading ? (
                            <div className="flex items-center justify-center">
                              <LoadingSpinner />
                              <span className="ml-2">Resetting password...</span>
                            </div>
                          ) : 'Reset Password'}
                        </Button>
                      </AnimatedButtonWrapper>
                    </AnimatedFormField>
                  </form>
                </FormSection>
              </>
            )}
            
            <AnimatedContainer variant="fadeIn" delay={0.7}>
              <div className="mt-6 text-center">
                <motion.p 
                  className="text-sm"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.8 }}
                >
                  Remember your password?{' '}
                  <motion.span
                    whileHover={{ 
                      scale: prefersReducedMotion ? 1 : 1.05,
                      color: "rgb(var(--primary))"
                    }}
                  >
                    <Link href="/auth/login" className="text-primary hover:underline">
                      Sign in
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