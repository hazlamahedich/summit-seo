import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MotionCard } from '@/components/ui/motion-card';
import { Flex } from '@/components/ui/flex';
import { 
  GripVertical,
  Maximize2,
  Minimize2,
  X,
  Settings,
  MoreVertical
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';
import { DashboardWidget as DashboardWidgetType } from '@/contexts/user-preferences-context';

export interface DashboardWidgetProps {
  widget: DashboardWidgetType;
  onRemove?: (id: string) => void;
  onSizeChange?: (id: string, size: 'small' | 'medium' | 'large') => void;
  onSettingsChange?: (id: string, settings: Record<string, any>) => void;
  isDraggable?: boolean;
  dragHandleProps?: any;
  className?: string;
  children: React.ReactNode;
}

export function DashboardWidget({ 
  widget,
  onRemove,
  onSizeChange,
  onSettingsChange,
  isDraggable = false,
  dragHandleProps,
  className,
  children
}: DashboardWidgetProps) {
  const [showSettings, setShowSettings] = useState(false);

  // Determine the correct size classes
  const sizeClasses = {
    small: 'col-span-1',
    medium: 'col-span-1 md:col-span-1 lg:col-span-1',
    large: 'col-span-1 md:col-span-2 lg:col-span-2'
  };

  // Calculate height based on size
  const heightClasses = {
    small: 'h-[200px]',
    medium: 'h-[250px]',
    large: 'h-[300px]'
  };

  const handleSizeToggle = () => {
    if (!onSizeChange) return;
    
    // Cycle through sizes: small -> medium -> large -> small
    const sizes: Array<'small' | 'medium' | 'large'> = ['small', 'medium', 'large'];
    const currentIndex = sizes.indexOf(widget.size);
    const nextSize = sizes[(currentIndex + 1) % sizes.length];
    
    onSizeChange(widget.id, nextSize);
  };

  return (
    <MotionCard
      variant="hover-lift"
      className={cn(
        'p-4 overflow-hidden',
        sizeClasses[widget.size],
        heightClasses[widget.size],
        className
      )}
    >
      <Flex direction="col" className="h-full">
        {/* Widget Header */}
        <Flex align="center" justify="between" className="mb-2">
          <Flex align="center" gap={2}>
            {isDraggable && (
              <div {...dragHandleProps} className="cursor-grab active:cursor-grabbing p-1">
                <GripVertical className="h-4 w-4 text-muted-foreground" />
              </div>
            )}
            <h3 className="font-medium">{widget.title}</h3>
          </Flex>
          
          <Flex align="center" gap={2}>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleSizeToggle}>
                  {widget.size === 'small' ? (
                    <Maximize2 className="h-4 w-4 mr-2" />
                  ) : (
                    <Minimize2 className="h-4 w-4 mr-2" />
                  )}
                  {widget.size === 'small' ? 'Increase Size' : 
                   widget.size === 'medium' ? 'Maximize' : 'Minimize'}
                </DropdownMenuItem>
                {onSettingsChange && (
                  <DropdownMenuItem onClick={() => setShowSettings(!showSettings)}>
                    <Settings className="h-4 w-4 mr-2" />
                    Widget Settings
                  </DropdownMenuItem>
                )}
                {onRemove && (
                  <DropdownMenuItem 
                    onClick={() => onRemove(widget.id)}
                    className="text-destructive focus:text-destructive"
                  >
                    <X className="h-4 w-4 mr-2" />
                    Remove Widget
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </Flex>
        </Flex>
        
        {/* Widget Content */}
        <div className="flex-1 overflow-auto">
          {children}
        </div>
      </Flex>
    </MotionCard>
  );
} 