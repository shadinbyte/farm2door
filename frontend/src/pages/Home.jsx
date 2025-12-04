import { Link } from 'react-router-dom'
import Layout from '@/components/common/Layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Truck, Leaf, Shield, Clock } from 'lucide-react'

const Home = () => {
  const featuredProducts = [
    {
      id: 1,
      name: 'Organic Tomatoes',
      price: 4.99,
      image: '🍅',
      category: 'Vegetables'
    },
    {
      id: 2,
      name: 'Fresh Strawberries',
      price: 6.99,
      image: '🍓',
      category: 'Fruits'
    },
    {
      id: 3,
      name: 'Farm Eggs',
      price: 5.99,
      image: '🥚',
      category: 'Dairy'
    },
    {
      id: 4,
      name: 'Green Lettuce',
      price: 3.49,
      image: '🥬',
      category: 'Vegetables'
    }
  ]

  const features = [
    {
      icon: <Truck className="h-8 w-8" />,
      title: 'Free Delivery',
      description: 'Free shipping on orders over $50'
    },
    {
      icon: <Leaf className="h-8 w-8" />,
      title: '100% Organic',
      description: 'Certified organic products from local farms'
    },
    {
      icon: <Shield className="h-8 w-8" />,
      title: 'Quality Guarantee',
      description: 'Fresh products or your money back'
    },
    {
      icon: <Clock className="h-8 w-8" />,
      title: 'Same Day Delivery',
      description: 'Order before 2 PM for same-day delivery'
    }
  ]

  return (
    <Layout>
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-green-50 to-green-100 dark:from-green-950 dark:to-green-900">
        <div className="container mx-auto px-4 py-20">
          <div className="max-w-3xl">
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              Fresh From Farm to Your Door
            </h1>
            <p className="text-xl text-muted-foreground mb-8">
              Experience the taste of locally sourced, organic produce delivered fresh daily.
              Support local farmers while enjoying the best quality food.
            </p>
            <div className="flex gap-4">
              <Link to="/shop">
                <Button size="lg" className="text-lg px-8">
                  Shop Now
                </Button>
              </Link>
              <Link to="/about">
                <Button size="lg" variant="outline" className="text-lg px-8">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="text-center">
                <CardContent className="pt-6">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary mb-4">
                    {feature.icon}
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products Section */}
      <section className="py-16 bg-muted/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Featured Products</h2>
            <p className="text-muted-foreground">Handpicked fresh produce from our local farms</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuredProducts.map((product) => (
              <Card key={product.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                <div className="aspect-square bg-gradient-to-br from-green-100 to-green-50 flex items-center justify-center text-8xl">
                  {product.image}
                </div>
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground mb-1">{product.category}</p>
                  <h3 className="font-semibold mb-2">{product.name}</h3>
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold text-primary">${product.price}</span>
                    <Link to={`/product/${product.id}`}>
                      <Button size="sm">View</Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="text-center mt-8">
            <Link to="/shop">
              <Button size="lg" variant="outline">View All Products</Button>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <Card className="bg-primary text-primary-foreground">
            <CardContent className="p-12 text-center">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Start Your Fresh Journey Today
              </h2>
              <p className="text-lg mb-8 opacity-90">
                Join thousands of happy customers enjoying fresh, organic produce
              </p>
              <Link to="/register">
                <Button size="lg" variant="secondary" className="text-lg px-8">
                  Create Account
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </section>
    </Layout>
  )
}

export default Home
