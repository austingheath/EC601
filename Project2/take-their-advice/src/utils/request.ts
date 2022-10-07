export type RequestSupportedMimeType = 'application/json' | 'text/plain';
export type RequestQueryParamValue = string | number | boolean | object | null | undefined;
export type RequestMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
export type Request = {
  url: string;
  responseMimeType?: RequestSupportedMimeType;
  method?: RequestMethod;
  body?: object | string;
  // query?: Record<string, RequestQueryParamValue>;
  headers?: Headers;
};

// Make an HTTP request
export async function request(req: Request) {
  const { url, responseMimeType = 'application/json', method = 'GET', body, headers } = req;

  // Build query string
  // let queryString = '';
  // if (query != null) {
  //   queryString = Object.entries(query).map(([key, value]) => );
  // }

  // Build body
  const convertedBody = typeof body === 'object' ? JSON.stringify(body) : body;

  // Make request
  const response = await fetch(url, {
    method,
    headers,
    body: convertedBody,
  });

  // Parse response from content type, otherwise use responseMimeType
  const contentType = response.headers.get('Content-Type');
  const mimeType = contentType != null ? contentType.split(';')[0].trim() : responseMimeType;

  switch (mimeType) {
    case 'application/json': {
      return response.json();
    }
    case 'text/plain': {
      return response.text();
    }
    default: {
      throw new Error(`Mime type ${mimeType} not supported`);
    }
  }
}
