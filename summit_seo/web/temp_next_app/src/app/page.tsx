import { AnimatedContainer } from '@/components/ui/animated-container';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { Section } from '@/components/ui/section';
import { Container } from '@/components/ui/container';
import { Grid, GridItem } from '@/components/ui/grid';
import { Flex } from '@/components/ui/flex';

export default function Home() {
  return (
    <>
      <Section size="xl" className="relative overflow-hidden">
        <Container>
          <Grid cols={{ default: 1, md: 2 }} gap={8} className="items-center">
            <GridItem>
              <AnimatedContainer
                variant="slideRight"
                delay={0.2}
                className="space-y-6"
              >
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight">
                  Elevate Your SEO Performance
                </h1>
                <p className="text-xl text-muted-foreground">
                  Comprehensive analysis and AI-powered recommendations to improve your website's visibility.
                </p>
                <div className="flex flex-wrap gap-4 pt-4">
                  <Button asChild size="lg">
                    <Link href="/signup">Get Started</Link>
                  </Button>
                  <Button asChild variant="outline" size="lg">
                    <Link href="/features">Learn More</Link>
                  </Button>
                </div>
              </AnimatedContainer>
            </GridItem>
            
            <GridItem className="relative">
              <AnimatedContainer
                variant="slideLeft"
                delay={0.4}
                className="bg-card p-6 rounded-lg shadow-lg border border-border"
              >
                <div className="space-y-4">
                  <h2 className="text-2xl font-semibold">Quick Analysis</h2>
                  <div className="space-y-3">
                    <div>
                      <label htmlFor="url" className="block text-sm font-medium mb-1">
                        Enter your website URL
                      </label>
                      <input
                        type="url"
                        id="url"
                        placeholder="https://example.com"
                        className="w-full px-3 py-2 border rounded-md"
                      />
                    </div>
                    <Button className="w-full">Analyze Now</Button>
                    <p className="text-xs text-muted-foreground text-center">
                      Free analysis with limited results. Sign up for full access.
                    </p>
                  </div>
                </div>
              </AnimatedContainer>
            </GridItem>
          </Grid>
        </Container>
      </Section>

      <Section className="bg-muted/30">
        <Container>
          <AnimatedContainer
            variant="fadeIn"
            delay={0.2}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold mb-4">Key Features</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Our comprehensive SEO platform provides everything you need to improve your search rankings.
            </p>
          </AnimatedContainer>

          <Grid cols={{ default: 1, md: 2, lg: 3 }} gap={6}>
            {[
              {
                title: "Technical SEO Analysis",
                description: "Identify technical issues that may impact your site's performance in search results."
              },
              {
                title: "Content Optimization",
                description: "Get recommendations to optimize your content for better search engine visibility."
              },
              {
                title: "Keyword Research",
                description: "Discover high-value keywords that can drive more traffic to your website."
              },
              {
                title: "Competitor Analysis",
                description: "Learn from your competitors and identify opportunities to outrank them."
              },
              {
                title: "Performance Metrics",
                description: "Track your SEO performance over time with detailed analytics and reports."
              },
              {
                title: "AI Recommendations",
                description: "Receive intelligent suggestions powered by advanced machine learning algorithms."
              }
            ].map((feature, index) => (
              <AnimatedContainer
                key={index}
                variant="fadeIn"
                delay={0.2 + index * 0.1}
                className="bg-card p-6 rounded-lg border border-border h-full"
              >
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </AnimatedContainer>
            ))}
          </Grid>
        </Container>
      </Section>

      <Section size="lg">
        <Container>
          <Flex direction="col" align="center" className="text-center">
            <AnimatedContainer
              variant="fadeIn"
              delay={0.2}
              className="max-w-2xl"
            >
              <h2 className="text-3xl font-bold mb-4">Ready to improve your SEO?</h2>
              <p className="text-xl text-muted-foreground mb-8">
                Join thousands of businesses that have improved their search rankings with Summit SEO.
              </p>
              <Button asChild size="lg">
                <Link href="/signup">Get Started Now</Link>
              </Button>
            </AnimatedContainer>
          </Flex>
        </Container>
      </Section>
    </>
  );
}
