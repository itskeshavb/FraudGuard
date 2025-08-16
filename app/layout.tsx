import './globals.css'

export const metadata = {
  title: 'FraudGuard - AI Fraud Detection',
  description: 'Detect fraudulent transactions with AI-powered analysis',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
