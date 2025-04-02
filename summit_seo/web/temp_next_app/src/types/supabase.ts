export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      // Add existing tables here
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
  ab_testing: {
    Tables: {
      ab_experiments: {
        Row: {
          id: string
          name: string
          description: string | null
          active: boolean
          start_date: string
          end_date: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          name: string
          description?: string | null
          active?: boolean
          start_date?: string
          end_date?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          name?: string
          description?: string | null
          active?: boolean
          start_date?: string
          end_date?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      ab_variants: {
        Row: {
          id: string
          experiment_id: string
          name: string
          weight: number
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          experiment_id: string
          name: string
          weight?: number
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          experiment_id?: string
          name?: string
          weight?: number
          created_at?: string
          updated_at?: string
        }
      }
      ab_user_experiments: {
        Row: {
          id: string
          user_id: string
          experiment_id: string
          variant_id: string
          assigned_at: string
          last_interaction: string | null
          interactions: number
          converted: boolean
        }
        Insert: {
          id?: string
          user_id: string
          experiment_id: string
          variant_id: string
          assigned_at?: string
          last_interaction?: string | null
          interactions?: number
          converted?: boolean
        }
        Update: {
          id?: string
          user_id?: string
          experiment_id?: string
          variant_id?: string
          assigned_at?: string
          last_interaction?: string | null
          interactions?: number
          converted?: boolean
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      update_modified_column: {
        Args: Record<PropertyKey, never>
        Returns: unknown
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
  auth: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          created_at: string
        }
        Insert: {
          id?: string
          email: string
          created_at?: string
        }
        Update: {
          id?: string
          email?: string
          created_at?: string
        }
      }
      roles: {
        Row: {
          id: string
          user_id: string
          role: string
        }
        Insert: {
          id?: string
          user_id: string
          role: string
        }
        Update: {
          id?: string
          user_id?: string
          role?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
} 