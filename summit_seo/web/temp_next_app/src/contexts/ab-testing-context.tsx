'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { Database } from '@/types/supabase';

// Define types for AB testing
export interface Experiment {
  id: string;
  name: string;
  description: string | null;
  active: boolean;
  start_date: string;
  end_date: string | null;
  created_at: string;
  updated_at: string;
  variants: Variant[];
}

export interface Variant {
  id: string;
  experiment_id: string;
  name: string;
  weight: number;
  created_at: string;
  updated_at: string;
}

export interface UserExperiment {
  id: string;
  user_id: string;
  experiment_id: string;
  variant_id: string;
  assigned_at: string;
  last_interaction: string | null;
  interactions: number;
  converted: boolean;
}

interface ABTestingContextType {
  // Data
  experiments: Experiment[];
  userExperiments: UserExperiment[];
  loading: boolean;
  isDevelopmentMode: boolean;
  
  // Methods
  loadExperiments: () => Promise<void>;
  loadUserExperiments: () => Promise<void>;
  assignUserToExperiment: (experimentId: string) => Promise<string | null>;
  getAssignedVariant: (experimentId: string) => string | null;
  trackInteraction: (experimentId: string) => Promise<void>;
  trackConversion: (experimentId: string) => Promise<void>;
  isUserInExperiment: (experimentId: string) => boolean;
  createExperiment: (name: string, description: string | null, variants: Omit<Variant, 'id' | 'experiment_id' | 'created_at' | 'updated_at'>[]) => Promise<string | null>;
}

// Development mode fixed user ID
const DEV_USER_ID = '00000000-0000-0000-0000-000000000000';

const ABTestingContext = createContext<ABTestingContextType | undefined>(undefined);

interface ABTestingProviderProps {
  children: ReactNode;
  devMode?: boolean;
}

export function ABTestingProvider({ children, devMode = true }: ABTestingProviderProps) {
  const supabase = createClientComponentClient<Database>();
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [userExperiments, setUserExperiments] = useState<UserExperiment[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isDevelopmentMode] = useState<boolean>(devMode);

  useEffect(() => {
    loadExperiments();
    loadUserExperiments();
  }, []);

  const loadExperiments = async () => {
    try {
      setLoading(true);
      
      // Fetch active experiments
      const { data: experimentsData, error: experimentsError } = await supabase
        .from('ab_experiments')
        .select('*')
        .eq('active', true);
      
      if (experimentsError) {
        console.error('Error loading experiments:', experimentsError);
        return;
      }

      // Fetch variants for each experiment
      const experimentsWithVariants = await Promise.all(
        experimentsData.map(async (experiment: Database['ab_testing']['Tables']['ab_experiments']['Row']) => {
          const { data: variantsData, error: variantsError } = await supabase
            .from('ab_variants')
            .select('*')
            .eq('experiment_id', experiment.id);
          
          if (variantsError) {
            console.error(`Error loading variants for experiment ${experiment.id}:`, variantsError);
            return { ...experiment, variants: [] };
          }
          
          return { ...experiment, variants: variantsData };
        })
      );

      setExperiments(experimentsWithVariants);
    } catch (error) {
      console.error('Error in loadExperiments:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUserExperiments = async () => {
    try {
      setLoading(true);
      
      // Get current user
      const { data: { user } } = await supabase.auth.getUser();
      const currentUserId = user?.id || (isDevelopmentMode ? DEV_USER_ID : null);
      
      if (!currentUserId) {
        return;
      }

      // Fetch user's experiment assignments
      const { data: userExperimentsData, error: userExperimentsError } = await supabase
        .from('ab_user_experiments')
        .select('*')
        .eq('user_id', currentUserId);
      
      if (userExperimentsError) {
        console.error('Error loading user experiments:', userExperimentsError);
        return;
      }

      setUserExperiments(userExperimentsData || []);
    } catch (error) {
      console.error('Error in loadUserExperiments:', error);
    } finally {
      setLoading(false);
    }
  };

  const createExperiment = async (
    name: string, 
    description: string | null, 
    variants: Omit<Variant, 'id' | 'experiment_id' | 'created_at' | 'updated_at'>[]
  ): Promise<string | null> => {
    try {
      // Create experiment
      const { data: newExperiment, error: experimentError } = await supabase
        .from('ab_experiments')
        .insert({
          name,
          description,
          active: true,
          start_date: new Date().toISOString()
        })
        .select('*')
        .single();
        
      if (experimentError || !newExperiment) {
        console.error('Error creating experiment:', experimentError);
        return null;
      }
      
      // Create variants
      const variantsWithExperimentId = variants.map(variant => ({
        ...variant,
        experiment_id: newExperiment.id
      }));
      
      const { data: newVariants, error: variantsError } = await supabase
        .from('ab_variants')
        .insert(variantsWithExperimentId)
        .select('*');
        
      if (variantsError) {
        console.error('Error creating variants:', variantsError);
        // Rollback experiment creation
        await supabase
          .from('ab_experiments')
          .delete()
          .eq('id', newExperiment.id);
        return null;
      }
      
      // Update local state
      const experimentWithVariants = {
        ...newExperiment,
        variants: newVariants
      };
      
      setExperiments(prev => [...prev, experimentWithVariants]);
      
      return newExperiment.id;
    } catch (error) {
      console.error('Error in createExperiment:', error);
      return null;
    }
  };

  const assignUserToExperiment = async (experimentId: string): Promise<string | null> => {
    try {
      // Get current user
      const { data: { user } } = await supabase.auth.getUser();
      const currentUserId = user?.id || (isDevelopmentMode ? DEV_USER_ID : null);
      
      if (!currentUserId) {
        return null;
      }

      // Check if user is already assigned to this experiment
      const existingAssignment = userExperiments.find(
        (ue) => ue.experiment_id === experimentId && ue.user_id === currentUserId
      );

      if (existingAssignment) {
        return existingAssignment.variant_id;
      }

      // Get experiment and its variants
      const experiment = experiments.find(e => e.id === experimentId);
      if (!experiment || !experiment.variants || experiment.variants.length === 0) {
        return null;
      }
      
      // Randomly assign user to a variant based on weights
      const totalWeight = experiment.variants.reduce((sum, variant) => sum + variant.weight, 0);
      let randomNum = Math.random() * totalWeight;
      let selectedVariant: Variant | null = null;
      
      for (const variant of experiment.variants) {
        randomNum -= variant.weight;
        if (randomNum <= 0) {
          selectedVariant = variant;
          break;
        }
      }
      
      // If no variant was selected (shouldn't happen if weights are valid), use the first one
      if (!selectedVariant) {
        selectedVariant = experiment.variants[0];
      }

      // Save the assignment
      const newAssignment = {
        user_id: currentUserId,
        experiment_id: experimentId,
        variant_id: selectedVariant.id,
        interactions: 0,
        converted: false
      };

      const { data, error } = await supabase
        .from('ab_user_experiments')
        .insert(newAssignment)
        .select('*')
        .single();
      
      if (error) {
        console.error('Error assigning user to experiment:', error);
        return null;
      }

      // Update local state
      setUserExperiments([...userExperiments, data]);
      return selectedVariant.id;
    } catch (error) {
      console.error('Error in assignUserToExperiment:', error);
      return null;
    }
  };

  const getAssignedVariant = (experimentId: string): string | null => {
    // Get current user's assigned variant for the experiment
    const userExperiment = userExperiments.find(ue => ue.experiment_id === experimentId);
    return userExperiment ? userExperiment.variant_id : null;
  };

  const trackInteraction = async (experimentId: string): Promise<void> => {
    try {
      // Get current user
      const { data: { user } } = await supabase.auth.getUser();
      const currentUserId = user?.id || (isDevelopmentMode ? DEV_USER_ID : null);
      
      if (!currentUserId) {
        return;
      }

      // Find the user experiment record
      const userExperiment = userExperiments.find(
        (ue) => ue.experiment_id === experimentId && ue.user_id === currentUserId
      );
      
      if (!userExperiment) {
        return;
      }

      // Update the interactions count
      const { error } = await supabase
        .from('ab_user_experiments')
        .update({
          interactions: userExperiment.interactions + 1,
          last_interaction: new Date().toISOString()
        })
        .eq('id', userExperiment.id);
      
      if (error) {
        console.error('Error tracking interaction:', error);
        return;
      }

      // Update local state
      setUserExperiments(
        userExperiments.map(ue => 
          ue.id === userExperiment.id 
            ? { 
                ...ue, 
                interactions: ue.interactions + 1,
                last_interaction: new Date().toISOString()
              } 
            : ue
        )
      );
    } catch (error) {
      console.error('Error in trackInteraction:', error);
    }
  };

  const trackConversion = async (experimentId: string): Promise<void> => {
    try {
      // Get current user
      const { data: { user } } = await supabase.auth.getUser();
      const currentUserId = user?.id || (isDevelopmentMode ? DEV_USER_ID : null);
      
      if (!currentUserId) {
        return;
      }

      // Find the user experiment record
      const userExperiment = userExperiments.find(
        (ue) => ue.experiment_id === experimentId && ue.user_id === currentUserId
      );
      
      if (!userExperiment) {
        return;
      }

      // Update the conversion status
      const { error } = await supabase
        .from('ab_user_experiments')
        .update({
          converted: true,
          last_interaction: new Date().toISOString()
        })
        .eq('id', userExperiment.id);
      
      if (error) {
        console.error('Error tracking conversion:', error);
        return;
      }

      // Update local state
      setUserExperiments(
        userExperiments.map(ue => 
          ue.id === userExperiment.id 
            ? { 
                ...ue, 
                converted: true,
                last_interaction: new Date().toISOString()
              } 
            : ue
        )
      );
    } catch (error) {
      console.error('Error in trackConversion:', error);
    }
  };

  const isUserInExperiment = (experimentId: string): boolean => {
    // Check if user is participating in the experiment
    return userExperiments.some(ue => ue.experiment_id === experimentId);
  };

  const value = {
    experiments,
    userExperiments,
    loading,
    isDevelopmentMode,
    loadExperiments,
    loadUserExperiments,
    assignUserToExperiment,
    getAssignedVariant,
    trackInteraction,
    trackConversion,
    isUserInExperiment,
    createExperiment
  };

  return (
    <ABTestingContext.Provider value={value}>
      {children}
    </ABTestingContext.Provider>
  );
}

export function useABTesting() {
  const context = useContext(ABTestingContext);
  if (context === undefined) {
    throw new Error('useABTesting must be used within an ABTestingProvider');
  }
  return context;
} 