"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, Loader2 } from "lucide-react";

// Define what a Product looks like (matching your API response)
interface Product {
  title: string;
  brand: string;
  price: number;
  match_score: number;
  url: string;
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query) return;
    setLoading(true);
    
    try {
      // Call your Python API
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/search?q=${query}`);
      const data = await res.json();
      setResults(data);
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-8 bg-slate-50">
      <div className="w-full max-w-2xl space-y-8">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900">
            Skincare Intelligence
          </h1>
          <p className="text-slate-500">
            Find dupes and deals across Nykaa, Minimalist, and more.
          </p>
        </div>

        {/* Search Bar */}
        <div className="flex w-full space-x-2">
          <Input 
            type="text" 
            placeholder="Search for 'vitamin c serum' or 'acne scars'..." 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            className="h-12"
          />
          <Button onClick={handleSearch} size="lg" disabled={loading}>
            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Search className="mr-2 h-4 w-4" />}
            Search
          </Button>
        </div>

        {/* Results Grid */}
        <div className="grid grid-cols-1 gap-4">
          {results.map((product, idx) => (
            <Card key={idx} className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div className="space-y-1">
                  <Badge variant="secondary" className="mb-1">{product.brand}</Badge>
                  <CardTitle className="text-lg font-medium leading-tight">
                    {product.title}
                  </CardTitle>
                </div>
                <div className="text-xl font-bold text-green-600">
                  ₹{product.price}
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex justify-between items-center mt-2">
                  <span className="text-sm text-slate-500">
                    Match Score: {Math.round(product.match_score * 100)}%
                  </span>
                  <a 
                    href={product.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-sm font-medium text-blue-600 hover:underline"
                  >
                    View Deal →
                  </a>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </main>
  );
}