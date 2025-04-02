import { 
  BarChart, 
  Calendar, 
  CreditCard, 
  Home, 
  Settings, 
  User, 
  Users, 
  Activity,
  Gauge,
  ChevronRight,
  ChevronLeft,
  Brain,
} from "lucide-react";

const navItems = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: Home,
    label: "Dashboard",
  },
  {
    title: "Projects",
    href: "/dashboard/projects",
    icon: Users,
    label: "Projects",
  },
  {
    title: "Analyses",
    href: "/dashboard/analyses",
    icon: Activity,
    label: "Analyses",
  },
  {
    title: "AI Insights",
    href: "/dashboard/insights",
    icon: Brain,
    label: "AI Insights",
  },
  {
    title: "Metrics",
    href: "/dashboard/metrics",
    icon: Gauge,
    label: "Metrics",
  },
  {
    title: "Engagement",
    href: "/dashboard/engagement",
    icon: BarChart,
    label: "Engagement",
  },
  {
    title: "Settings",
    href: "/dashboard/settings",
    icon: Settings,
    label: "Settings",
  },
]; 