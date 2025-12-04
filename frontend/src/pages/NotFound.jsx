import { Link } from 'react-router-dom'
import Layout from '@/components/common/Layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Home, Search } from 'lucide-react'

const NotFound = () => {
  return (
    <Layout>
      <div className="container mx-auto px-4 py-16">
        <Card className="max-w-2xl mx-auto">
          <CardContent className="p-12 text-center">
            <div className="text-9xl font-bold text-primary mb-4">404</div>
            <h1 className="text-4xl font-bold mb-4">Page Not Found</h1>
            <p className="text-muted-foreground mb-8">
              Oops! The page you're looking for doesn't exist. It might have been moved or deleted.
            </p>
            <div className="flex gap-4 justify-center">
              <Link to="/">
                <Button size="lg">
                  <Home className="mr-2 h-5 w-5" />
                  Go Home
                </Button>
              </Link>
              <Link to="/shop">
                <Button size="lg" variant="outline">
                  <Search className="mr-2 h-5 w-5" />
                  Browse Shop
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  )
}

export default NotFound
