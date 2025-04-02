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
  AnimatedButtonWrapper,
  LoadingSpinner,
  FormSection
} from '@/components/ui/auth-animated-elements';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const router = useRouter();
  const { signUp, user } = useAuth();
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
    
    // Validate password match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    // Validate password strength
    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }
    
    setIsLoading(true);

    try {
      const { error: signUpError } = await signUp(email, password);
      
      if (signUpError) {
        setError(signUpError.message || 'Failed to create account');
        return;
      }
      
      // Registration successful, redirect to login with a success message
      router.push('/auth/login?registered=true');
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
                Create Account
              </motion.h1>
            </AnimatedContainer>
            
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
                  <AnimatedLabel htmlFor="password">
                    Password
                  </AnimatedLabel>
                  <AnimatedInput
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                    placeholder="Create a strong password"
                    required
                  />
                  <motion.p 
                    className="text-sm text-muted-foreground mt-1"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                  >
                    Password must be at least 8 characters.
                  </motion.p>
                </AnimatedFormField>
                
                <AnimatedFormField delay={0.5}>
                  <AnimatedLabel htmlFor="confirmPassword">
                    Confirm Password
                  </AnimatedLabel>
                  <AnimatedInput
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm your password"
                    required
                  />
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
                          <span className="ml-2">Creating account...</span>
                        </div>
                      ) : 'Create account'}
                    </Button>
                  </AnimatedButtonWrapper>
                </AnimatedFormField>
              </form>
            </FormSection>
            
            <AnimatedContainer variant="fadeIn" delay={0.7}>
              <div className="mt-6 text-center">
                <motion.p 
                  className="text-sm"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.8 }}
                >
                  Already have an account?{' '}
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