"use client"

import * as React from "react"
import { Mail, Search, Info, AlertCircle, CheckCircle2 } from "lucide-react"

import { AnimatedButton } from "@/components/ui/animated-button"
import { AnimatedCard } from "@/components/ui/animated-card"
import { AnimatedInput } from "@/components/ui/animated-input"
import { Button } from "@/components/ui/button"

export function AnimationExample() {
  const [buttonLoading, setButtonLoading] = React.useState(false)
  const [buttonFeedback, setButtonFeedback] = React.useState<"success" | "error" | "none">("none")
  const [formData, setFormData] = React.useState({
    email: "",
    name: "",
    website: ""
  })
  const [formErrors, setFormErrors] = React.useState({
    email: "",
    name: "",
    website: ""
  })
  
  // Mock toast function since we don't have access to the real one
  const showToast = (message: string, type: string) => {
    console.log(`[Toast - ${type}]: ${message}`)
    // In a real application, this would use the toast component
  }
  
  const validateForm = () => {
    const errors = {
      email: "",
      name: "",
      website: ""
    }
    let isValid = true
    
    // Validate name
    if (!formData.name || formData.name.length < 2) {
      errors.name = "Name must be at least 2 characters"
      isValid = false
    }
    
    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!formData.email || !emailRegex.test(formData.email)) {
      errors.email = "Please enter a valid email address"
      isValid = false
    }
    
    // Validate website (if provided)
    if (formData.website) {
      try {
        new URL(formData.website)
      } catch (e) {
        errors.website = "Please enter a valid URL"
        isValid = false
      }
    }
    
    setFormErrors(errors)
    return isValid
  }
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    // Clear error when typing
    if (formErrors[name as keyof typeof formErrors]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ""
      }))
    }
  }
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      setButtonFeedback("error")
      setTimeout(() => setButtonFeedback("none"), 1500)
      return
    }
    
    setButtonLoading(true)
    
    // Simulate API call
    try {
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // Successful submission
      setButtonFeedback("success")
      showToast(`Analysis Requested! We'll send the results to ${formData.email}`, "success")
      
      // Reset form
      setTimeout(() => {
        setFormData({ email: "", name: "", website: "" })
        setButtonFeedback("none")
      }, 1000)
    } catch (error) {
      // Error handling
      setButtonFeedback("error")
      showToast("Something went wrong. Please try again later", "error")
    } finally {
      setButtonLoading(false)
    }
  }
  
  return (
    <div className="space-y-8 p-4">
      <h2 className="text-2xl font-bold">Animated UI Components</h2>
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Card Example - Default */}
        <AnimatedCard>
          <h3 className="text-lg font-medium mb-2">Default Card</h3>
          <p className="text-muted-foreground">
            This card animates on hover with subtle elevation changes.
          </p>
        </AnimatedCard>
        
        {/* Card Example - Interactive */}
        <AnimatedCard variant="interactive" onClick={() => showToast("Card clicked!", "info")}>
          <h3 className="text-lg font-medium mb-2">Interactive Card</h3>
          <p className="text-muted-foreground">
            Click me! This card shows the user it's clickable with hover effects.
          </p>
        </AnimatedCard>
        
        {/* Card Example - Highlight */}
        <AnimatedCard variant="highlight">
          <h3 className="text-lg font-medium mb-2">Highlight Card</h3>
          <p className="text-muted-foreground">
            This card stands out with a highlighted border.
          </p>
        </AnimatedCard>
      </div>
      
      <div className="space-y-4 py-4">
        <h3 className="text-xl font-medium">Animated Buttons</h3>
        <div className="flex flex-wrap gap-4">
          <AnimatedButton>Default Button</AnimatedButton>
          <AnimatedButton variant="secondary" icon={<Info className="h-4 w-4" />}>
            With Icon
          </AnimatedButton>
          <AnimatedButton variant="outline" icon={<CheckCircle2 className="h-4 w-4" />} iconPosition="right">
            Icon Right
          </AnimatedButton>
          <AnimatedButton loading>Loading State</AnimatedButton>
          <AnimatedButton feedback="success">Success State</AnimatedButton>
          <AnimatedButton feedback="error">Error State</AnimatedButton>
        </div>
      </div>
      
      <div className="space-y-6">
        <h3 className="text-xl font-medium">Animated Form</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <AnimatedInput 
              name="name"
              label="Name" 
              placeholder="Enter your name" 
              icon={<Info className="h-4 w-4" />}
              error={formErrors.name}
              value={formData.name}
              onChange={handleChange}
            />
          </div>
          
          <div>
            <AnimatedInput 
              name="email"
              label="Email" 
              placeholder="Enter your email" 
              icon={<Mail className="h-4 w-4" />}
              error={formErrors.email}
              value={formData.email}
              onChange={handleChange}
            />
          </div>
          
          <div>
            <AnimatedInput 
              name="website"
              label="Website (optional)" 
              placeholder="https://example.com" 
              icon={<Search className="h-4 w-4" />}
              hint="Enter your website to analyze"
              error={formErrors.website}
              success={formData.website !== "" && !formErrors.website}
              value={formData.website}
              onChange={handleChange}
            />
          </div>
          
          <div className="pt-4">
            <AnimatedButton 
              type="submit" 
              loading={buttonLoading} 
              loadingText="Submitting..."
              feedback={buttonFeedback}
              icon={buttonFeedback === "success" ? <CheckCircle2 className="h-4 w-4" /> : buttonFeedback === "error" ? <AlertCircle className="h-4 w-4" /> : undefined}
            >
              Submit Form
            </AnimatedButton>
          </div>
        </form>
      </div>
    </div>
  )
} 