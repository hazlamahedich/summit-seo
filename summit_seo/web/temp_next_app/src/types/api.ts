/**
 * API response structure
 */
export interface ApiResponse<T> {
  data: T | null;
  error: string | null;
}

/**
 * Pagination metadata
 */
export interface PaginationMeta {
  total: number;
  page: number;
  pages: number;
  page_size: number;
}

/**
 * Paginated response structure
 */
export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationMeta;
}

/**
 * Sort direction
 */
export type SortDirection = 'asc' | 'desc';

/**
 * Filter operator
 */
export type FilterOperator = 
  | 'eq' 
  | 'neq' 
  | 'gt' 
  | 'gte' 
  | 'lt' 
  | 'lte' 
  | 'like' 
  | 'ilike'
  | 'in'
  | 'contains';

/**
 * Filter criteria
 */
export interface FilterCriteria {
  field: string;
  operator: FilterOperator;
  value: any;
}

/**
 * Sorting criteria
 */
export interface SortCriteria {
  field: string;
  direction: SortDirection;
}

/**
 * Query parameters for paginated requests
 */
export interface PaginationParams {
  page?: number;
  page_size?: number;
  search?: string;
  sort?: string; // Format: field:direction
  filter?: Record<string, any>; // Format depends on backend implementation
}

/**
 * Project entity
 */
export interface Project {
  id: string;
  name: string;
  description: string;
  url: string;
  tenant_id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  tags: string[];
  status: string;
  settings: Record<string, any>;
}

/**
 * Analysis status
 */
export enum AnalysisStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

/**
 * Severity level
 */
export enum SeverityLevel {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
  INFO = 'info'
}

/**
 * Analysis entity
 */
export interface Analysis {
  id: string;
  project_id: string;
  status: AnalysisStatus;
  progress: number;
  results: Record<string, any> | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  error: string | null;
  overall_score: number | null;
  analyzers: string[];
}

/**
 * Finding entity
 */
export interface Finding {
  id: string;
  analysis_id: string;
  analyzer: string;
  category: string;
  subcategory: string | null;
  severity: SeverityLevel;
  message: string;
  description: string | null;
  location: string | null;
  details: Record<string, any> | null;
  created_at: string;
}

/**
 * Recommendation priority
 */
export enum RecommendationPriority {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low'
}

/**
 * Recommendation entity
 */
export interface Recommendation {
  id: string;
  analysis_id: string;
  finding_id: string | null;
  analyzer: string;
  category: string;
  type: string;
  priority: RecommendationPriority;
  title: string;
  description: string;
  steps: string[] | null;
  resources: string[] | null;
  details: Record<string, any> | null;
  created_at: string;
  enhanced: boolean;
  enhanced_description: string | null;
}

/**
 * Insight status 
 */
export enum InsightStatus {
  PENDING = 'pending',
  GENERATED = 'generated',
  FAILED = 'failed'
}

/**
 * Insight type
 */
export interface Insight {
  id: string;
  analysis_id: string;
  type: string;
  title: string;
  content: string;
  status: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
} 