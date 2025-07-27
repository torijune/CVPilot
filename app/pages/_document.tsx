import Document, { Html, Head, Main, NextScript } from "next/document";
import React from "react";

export default class MyDocument extends Document {
  render() {
    return (
      <Html lang="ko">
        <Head>
          <title>CVPilot - AI-Powered Curriculum Vitae Advisor</title>
          <meta name="description" content="AI-powered curriculum vitae advisor for graduate school applications and research career development" />
          <meta name="keywords" content="CV advisor, curriculum vitae, graduate school, AI, research, CV analysis, paper trends" />
          <meta name="author" content="CVPilot" />
          <meta property="og:title" content="CVPilot - AI-Powered Curriculum Vitae Advisor" />
          <meta property="og:description" content="AI-powered curriculum vitae advisor for graduate school applications and research career development" />
          <meta property="og:type" content="website" />
          <link rel="icon" href="/favicon.ico" />
        </Head>
        <body>
          <Main />
          <NextScript />
        </body>
      </Html>
    );
  }
}

