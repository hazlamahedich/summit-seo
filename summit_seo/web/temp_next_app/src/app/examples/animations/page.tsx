import { Metadata } from 'next';
import AnimationShowcase from '@/components/examples/animation-showcase';

export const metadata: Metadata = {
  title: 'Animation Showcase | Summit SEO',
  description: 'Explore the micro-interactions and animation patterns used in Summit SEO',
};

export default function AnimationsPage() {
  return <AnimationShowcase />;
} 