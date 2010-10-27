/*
**    Copyright (C) 2003-2010 Institute for Systems Biology
**                            Seattle, Washington, USA.
**
**    This library is free software; you can redistribute it and/or
**    modify it under the terms of the GNU Lesser General Public
**    License as published by the Free Software Foundation; either
**    version 2.1 of the License, or (at your option) any later version.
**
**    This library is distributed in the hope that it will be useful,
**    but WITHOUT ANY WARRANTY; without even the implied warranty of
**    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
**    Lesser General Public License for more details.
**
**    You should have received a copy of the GNU Lesser General Public
**    License along with this library; if not, write to the Free Software
**    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
*/
package org.systemsbiology.addama.sandbox.transplants;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.MultiThreadedHttpConnectionManager;
import org.apache.commons.httpclient.methods.GetMethod;
import org.apache.commons.lang.StringUtils;
import org.systemsbiology.addama.commons.httpclient.support.ApiKeyHttpClientTemplate;
import org.systemsbiology.addama.commons.httpclient.support.GaeHostConfiguration;
import org.systemsbiology.addama.commons.httpclient.support.HttpClientTemplate;
import org.systemsbiology.addama.commons.httpclient.support.StatusCodeCaptureResponseCallback;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.net.URI;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;

/**
 * @author hrovira
 */
public class VerifyChromIndexes {
    private static HttpClientTemplate httpClientTemplate;

    public static void main(String[] args) throws Exception {
        initTemplate();

        BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(new File("/local/temp/bulkload/gene_synonyms_index.csv"))));

        int counter = 0;
        List<GetRunnable> getRunnables = new ArrayList<GetRunnable>();
        List<URI> targetUris = new ArrayList<URI>();

        String line = reader.readLine();
        while (line != null) {
            line = reader.readLine();
            if (line != null) {
                String[] splits = line.split(",");
                targetUris.add(new URI(StringUtils.replace(splits[0], "\"", "")));
                if (++counter % 100 == 0) {
                    getRunnables.add(new GetRunnable(targetUris));
                    targetUris = new ArrayList<URI>();
                }
            }
        }

        reader.close();

        for (GetRunnable getRunnable : getRunnables) {
            new Thread(getRunnable).start();
        }
    }

    private static void initTemplate() throws Exception {
        if (httpClientTemplate == null) {
            GaeHostConfiguration hostConfiguration = new GaeHostConfiguration();
            hostConfiguration.setSecureHostUrl(new URL("https://addama-systemsbiology-public.appspot.com"));
            hostConfiguration.afterPropertiesSet();

            HttpClient httpClient = new HttpClient();
            httpClient.setHostConfiguration(hostConfiguration);
            httpClient.setHttpConnectionManager(new MultiThreadedHttpConnectionManager());

            ApiKeyHttpClientTemplate template = new ApiKeyHttpClientTemplate(httpClient);
            template.setApikey("60667408-363a-45a5-b771-42a8e4ecc0a7");
            template.afterPropertiesSet();
            httpClientTemplate = template;
        }
    }

    private static class GetRunnable implements Runnable {
        private final HashSet<URI> goodEntries = new HashSet<URI>();
        private final HashSet<URI> missedEntries = new HashSet<URI>();
        private final List<URI> uris;

        private GetRunnable(List<URI> targeturis) {
            this.uris = targeturis;
        }

        public void run() {
            System.out.println("targetUris=" + uris.size());

            StatusCodeCaptureResponseCallback callback = new StatusCodeCaptureResponseCallback();
            for (URI uri : uris) {
                try {
                    GetMethod get = new GetMethod(uri.toString());
                    int statusCode = (Integer) httpClientTemplate.executeMethod(get, callback);
                    if (statusCode != 200) {
                        missedEntries.add(uri);
                    } else {
                        goodEntries.add(uri);
                    }
                } catch (Exception e) {
                    missedEntries.add(uri);
                }
            }

            System.out.println("goodEntries=" + goodEntries.size());
            System.err.println("missedEntries=" + missedEntries.size());
        }
    }
}