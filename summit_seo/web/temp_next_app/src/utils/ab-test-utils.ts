import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import type { Database } from '@/types/supabase';

interface CreateExperimentParams {
  name: string;
  description?: string;
  variants: {
    name: string;
    weight: number;
  }[];
}

/**
 * Creates a new A/B testing experiment with the specified variants
 */
export async function createExperiment({ 
  name, 
  description = null, 
  variants 
}: CreateExperimentParams): Promise<string | null> {
  try {
    const supabase = createClientComponentClient<Database>();
    
    // Create experiment
    const { data: experiment, error: experimentError } = await supabase
      .from('ab_experiments')
      .insert({
        name,
        description,
        active: true,
        start_date: new Date().toISOString()
      })
      .select('*')
      .single();
      
    if (experimentError || !experiment) {
      console.error('Error creating experiment:', experimentError);
      return null;
    }
    
    // Create variants
    const variantsWithExperimentId = variants.map(variant => ({
      ...variant,
      experiment_id: experiment.id
    }));
    
    const { error: variantsError } = await supabase
      .from('ab_variants')
      .insert(variantsWithExperimentId);
      
    if (variantsError) {
      console.error('Error creating variants:', variantsError);
      // Rollback experiment creation
      await supabase
        .from('ab_experiments')
        .delete()
        .eq('id', experiment.id);
      return null;
    }
    
    return experiment.id;
  } catch (error) {
    console.error('Error in createExperiment:', error);
    return null;
  }
}

/**
 * Gets experiment stats for a specific experiment
 */
export async function getExperimentStats(experimentId: string) {
  try {
    const supabase = createClientComponentClient<Database>();
    
    // Get experiment details
    const { data: experiment, error: experimentError } = await supabase
      .from('ab_experiments')
      .select('*')
      .eq('id', experimentId)
      .single();
    
    if (experimentError) {
      console.error('Error getting experiment:', experimentError);
      return null;
    }
    
    // Get variants
    const { data: variants, error: variantsError } = await supabase
      .from('ab_variants')
      .select('*')
      .eq('experiment_id', experimentId);
    
    if (variantsError) {
      console.error('Error getting variants:', variantsError);
      return null;
    }
    
    // Get user assignments for each variant
    const variantStats = await Promise.all(
      variants.map(async (variant) => {
        const { data: assignments, error: assignmentsError } = await supabase
          .from('ab_user_experiments')
          .select('*')
          .eq('variant_id', variant.id);
        
        if (assignmentsError) {
          console.error(`Error getting assignments for variant ${variant.id}:`, assignmentsError);
          return {
            variant,
            totalUsers: 0,
            interactionCount: 0,
            conversionCount: 0,
            conversionRate: 0
          };
        }
        
        const totalUsers = assignments?.length || 0;
        const interactionCount = assignments?.reduce((sum, a) => sum + (a.interactions || 0), 0) || 0;
        const conversionCount = assignments?.filter(a => a.converted).length || 0;
        const conversionRate = totalUsers > 0 ? (conversionCount / totalUsers) * 100 : 0;
        
        return {
          variant,
          totalUsers,
          interactionCount,
          conversionCount,
          conversionRate
        };
      })
    );
    
    return {
      experiment,
      variantStats
    };
  } catch (error) {
    console.error('Error in getExperimentStats:', error);
    return null;
  }
}

/**
 * Ends an experiment (sets active to false and sets end_date)
 */
export async function endExperiment(experimentId: string): Promise<boolean> {
  try {
    const supabase = createClientComponentClient<Database>();
    
    const { error } = await supabase
      .from('ab_experiments')
      .update({
        active: false,
        end_date: new Date().toISOString()
      })
      .eq('id', experimentId);
    
    if (error) {
      console.error('Error ending experiment:', error);
      return false;
    }
    
    return true;
  } catch (error) {
    console.error('Error in endExperiment:', error);
    return false;
  }
}

/**
 * Gets a development user ID for testing
 */
export function getDevUserId(): string {
  return '00000000-0000-0000-0000-000000000000';
} 