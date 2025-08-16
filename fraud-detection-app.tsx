"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { FileText, AlertCircle, CheckCircle2, Shield, TrendingUp, Activity, Info } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface Transaction {
  transaction_id?: string
  amount: number
  fraud_probability: number
  is_fraud: boolean
}

export default function FraudDetectionApp() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<Transaction[]>([])
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0]
    if (selectedFile && selectedFile.type === "text/csv") {
      setFile(selectedFile)
      setError(null)
    } else {
      setError("Please select a valid CSV file")
      setFile(null)
    }
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()

    if (!file) {
      setError("Please select a CSV file to upload")
      return
    }

    setLoading(true)
    setError(null)
    setResults([])

    try {
      const formData = new FormData()
      formData.append("file", file)

      const response = await fetch("/api/predict", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: Transaction[] = await response.json()
      setResults(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred while processing the data")
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount)
  }

  const formatProbability = (probability: number) => {
    return `${(probability * 100).toFixed(1)}%`
  }

  const fraudCount = results.filter((t) => t.is_fraud).length
  const legitimateCount = results.length - fraudCount

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-slate-900">
      {/* Navigation */}
      <nav className="border-b border-slate-800 bg-slate-900/95 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-blue-400" />
              <span className="ml-2 text-xl font-bold text-white">FraudGuard</span>
            </div>
          </div>
        </div>
      </nav>

      <div className="relative">
        {/* Hero Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <div className="text-center space-y-8">
            <div className="space-y-4">
              <h1 className="text-5xl md:text-6xl font-bold text-white leading-tight">The AI fraud detection agent</h1>
              <p className="text-xl text-slate-400 max-w-3xl mx-auto leading-relaxed">
                Detect fraudulent transactions faster, with an AI agent that analyzes patterns and identifies risks in
                real-time.
              </p>
            </div>

            {/* Process Steps */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16 max-w-4xl mx-auto">
              <Tooltip delayDuration={500}>
                <TooltipTrigger asChild>
                  <div className="text-center space-y-3 cursor-pointer">
                    <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mx-auto text-white font-bold text-lg">
                      1
                    </div>
                    <h3 className="text-lg font-semibold text-white">Upload Data</h3>
                    <p className="text-slate-400 text-sm">Upload CSV files containing transaction data</p>
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Click to upload your transaction CSV file</p>
                </TooltipContent>
              </Tooltip>
              <Tooltip delayDuration={500}>
                <TooltipTrigger asChild>
                  <div className="text-center space-y-3 cursor-pointer">
                    <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mx-auto text-white font-bold text-lg">
                      2
                    </div>
                    <h3 className="text-lg font-semibold text-white">Analyze</h3>
                    <p className="text-slate-400 text-sm">AI processes patterns and calculates fraud probability</p>
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Our AI analyzes transaction patterns and features</p>
                </TooltipContent>
              </Tooltip>
              <Tooltip delayDuration={500}>
                <TooltipTrigger asChild>
                  <div className="text-center space-y-3 cursor-pointer">
                    <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mx-auto text-white font-bold text-lg">
                      3
                    </div>
                    <h3 className="text-lg font-semibold text-white">Detect</h3>
                    <p className="text-slate-400 text-sm">Get detailed results with risk assessment</p>
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p>View fraud probability scores and risk assessment</p>
                </TooltipContent>
              </Tooltip>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        {results.length > 0 && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="bg-slate-800 border-slate-700">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-emerald-400 text-sm font-medium">Legitimate</p>
                      <p className="text-3xl font-bold text-white">{legitimateCount}</p>
                    </div>
                    <CheckCircle2 className="h-8 w-8 text-emerald-400" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-800 border-slate-700">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-red-400 text-sm font-medium">Fraudulent</p>
                      <p className="text-3xl font-bold text-white">{fraudCount}</p>
                    </div>
                    <AlertCircle className="h-8 w-8 text-red-400" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-800 border-slate-700">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-blue-400 text-sm font-medium">Total Analyzed</p>
                      <p className="text-3xl font-bold text-white">{results.length}</p>
                    </div>
                    <TrendingUp className="h-8 w-8 text-blue-400" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Analysis Section */}
        <div id="analysis-section" className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
          <Card className="bg-slate-800 border-slate-700 shadow-2xl">
            <CardHeader className="border-b border-slate-700">
              <CardTitle className="text-2xl text-white flex items-center gap-3">
                <Activity className="h-6 w-6 text-blue-400" />
                Transaction Analysis
              </CardTitle>
              <CardDescription className="text-slate-400">
                Upload a CSV file containing transaction data for fraud detection
              </CardDescription>
            </CardHeader>
            <CardContent className="p-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Label htmlFor="file-upload" className="text-lg font-semibold text-white">
                      Transaction File
                    </Label>
                    <Tooltip delayDuration={300}>
                      <TooltipTrigger asChild>
                        <Info className="h-5 w-5 text-slate-400 hover:text-blue-400 cursor-help transition-colors" />
                      </TooltipTrigger>
                      <TooltipContent className="max-w-sm">
                        <div className="space-y-2">
                          <p className="font-semibold">CSV Format Requirements:</p>
                          <ul className="text-xs space-y-1">
                            <li>• <strong>Required columns:</strong> TransactionID, TransactionDT, TransactionAmt, ProductCD</li>
                            <li>• <strong>Optional columns:</strong> card1-6, addr1-2, dist1-2, C1-14, D1-15, V1-339, M1-9</li>
                            <li>• <strong>Missing columns</strong> will be filled with default values</li>
                            <li>• <strong>File size:</strong> Maximum 10MB</li>
                          </ul>
                        </div>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <div className="flex flex-col gap-4">
                    <div className="relative">
                      <Input
                        id="file-upload"
                        type="file"
                        accept=".csv"
                        onChange={handleFileChange}
                        className="h-12 bg-slate-700 border-slate-600 text-slate-200 file:bg-blue-600 file:text-white file:border-0 file:rounded-md file:px-4 file:py-2 file:mr-4 file:h-8"
                      />
                    </div>
                    {file && (
                      <div className="flex items-center gap-2 text-sm bg-slate-700 text-slate-200 px-3 py-2 rounded-lg border border-slate-600 w-fit">
                        <FileText className="h-4 w-4" />
                        {file.name}
                      </div>
                    )}
                  </div>
                </div>

                {error && (
                  <Alert variant="destructive" className="bg-red-900/20 border-red-800 text-red-400">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <Tooltip delayDuration={500}>
                  <TooltipTrigger asChild>
                    <Button
                      type="submit"
                      disabled={loading || !file}
                      className="w-full h-12 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-lg"
                    >
                      {loading ? (
                        <div className="flex items-center justify-center">
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3" />
                          <span className="text-white">Analyzing Transactions...</span>
                        </div>
                      ) : (
                        <div className="flex items-center justify-center">
                          <Activity className="h-5 w-5 mr-2" />
                          <span className="text-white">Analyze Transactions</span>
                        </div>
                      )}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Click to start fraud detection analysis</p>
                  </TooltipContent>
                </Tooltip>
              </form>
            </CardContent>
          </Card>

          {/* Loading State */}
          {loading && (
            <Card className="mt-8 bg-slate-800 border-slate-700">
              <CardContent className="py-16">
                <div className="flex flex-col items-center justify-center space-y-6">
                  <div className="animate-spin rounded-full h-16 w-16 border-4 border-slate-600 border-t-blue-400"></div>
                  <div className="text-center space-y-2">
                    <p className="text-xl font-semibold text-slate-200">Analyzing transactions...</p>
                    <p className="text-sm text-slate-400">Our AI is processing your data for fraud patterns</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Results Section */}
          {results.length > 0 && (
            <Card className="mt-8 bg-slate-800 border-slate-700">
              <CardHeader className="border-b border-slate-700">
                <CardTitle className="text-xl text-white flex items-center gap-3">
                  <CheckCircle2 className="h-6 w-6 text-emerald-400" />
                  Analysis Results
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Comprehensive fraud analysis completed • {fraudCount} high-risk transactions identified
                </CardDescription>
              </CardHeader>
              <CardContent className="p-8">
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className="border-slate-700">
                        {results[0]?.transaction_id && (
                          <TableHead className="text-slate-300 font-semibold">Transaction ID</TableHead>
                        )}
                        <TableHead className="text-slate-300 font-semibold">Amount</TableHead>
                        <TableHead className="text-slate-300 font-semibold">Risk Assessment</TableHead>
                        <TableHead className="text-slate-300 font-semibold">Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {results.map((transaction, index) => (
                        <TableRow
                          key={transaction.transaction_id || index}
                          className="border-slate-700 hover:bg-slate-700/50 transition-colors"
                        >
                          {transaction.transaction_id && (
                            <TableCell className="font-mono text-sm text-slate-400">
                              {transaction.transaction_id}
                            </TableCell>
                          )}
                          <TableCell className="font-bold text-lg text-slate-200">
                            {formatCurrency(transaction.amount)}
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-3">
                              <div className="flex-1 bg-slate-700 rounded-full h-3 overflow-hidden">
                                <div
                                  className={`h-3 rounded-full transition-all duration-500 ${
                                    transaction.fraud_probability > 0.7
                                      ? "bg-red-500"
                                      : transaction.fraud_probability > 0.4
                                        ? "bg-yellow-500"
                                        : "bg-emerald-500"
                                  }`}
                                  style={{
                                    width: `${transaction.fraud_probability * 100}%`,
                                  }}
                                />
                              </div>
                              <span className="text-sm font-bold min-w-[60px] text-slate-300">
                                {formatProbability(transaction.fraud_probability)}
                              </span>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge
                              className={
                                transaction.is_fraud
                                  ? "bg-red-600 hover:bg-red-700 text-white border-0"
                                  : "bg-emerald-600 hover:bg-emerald-700 text-white border-0"
                              }
                            >
                              {transaction.is_fraud ? "Fraud" : "Legitimate"}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
    </TooltipProvider>
  )
}
