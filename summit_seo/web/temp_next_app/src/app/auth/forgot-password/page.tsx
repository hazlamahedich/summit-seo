'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
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

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  
  const router = useRouter();
  const { resetPassword, user } = useAuth();
  const prefersReducedMotion = useReducedMotion();
  
  // Redirect to dashboard if already logged in
  useEffect(() => {
    if (user) {
      router.push('/dashboard');
    }
  }, [user, router]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const { error: resetError } = await resetPassword(email);
      
      if (resetError) {
        setError(resetError.message || 'Failed to send reset email');
        return;
      }
      
      setSuccess(true);
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
            
            {!success ? (
              <>
                <AnimatedContainer variant="slideUp" delay={0.3}>
                  <motion.p 
                    className="text-muted-foreground mb-6 text-center"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                  >
                    Enter your email address and we'll send you a link to reset your password.
                  </motion.p>
                </AnimatedContainer>
                
                <AnimatedError message={error} className="mb-6" />
                
                <FormSection>
                  <form onSubmit={handleSubmit} className="space-y-5">
                    <AnimatedFormField delay={0.4}>
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
                              <span className="ml-2">Sending...</span>
                            </div>
                          ) : 'Send reset link'}
                        </Button>
                      </AnimatedButtonWrapper>
                    </AnimatedFormField>
                  </form>
                </FormSection>
              </>
            ) : (
              <AnimatedContainer variant="slideUp" delay={0.3}>
                <motion.div 
                  className="bg-success/15 text-success p-4 rounded-md mb-6"
                  initial={{ opacity: 0, y: -10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ 
                    type: "spring",
                    stiffness: 500,
                    damping: 30,
                    duration: prefersReducedMotion ? 0.1 : 0.5
                  }}
                >
                  <p className="font-medium">Check your email</p>
                  <p className="mt-1">
                    We've sent a password reset link to {email}. Please check your email and follow the instructions.
                  </p>
                </motion.div>
                <AnimatedButtonWrapper>
                  <Button 
                    className="w-full" 
                    onClick={() => router.push('/auth/login')}
                  >
                    Return to login
                  </Button>
                </AnimatedButtonWrapper>
              </AnimatedContainer>
            )}
            
            <AnimatedContainer variant="fadeIn" delay={0.6}>
              <div className="mt-6 text-center">
                <motion.p 
                  className="text-sm"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.7 }}
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