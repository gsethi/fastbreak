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

import org.apache.commons.httpclient.HttpMethod;
import org.apache.commons.httpclient.NameValuePair;
import org.apache.commons.httpclient.methods.GetMethod;
import org.apache.commons.httpclient.methods.PostMethod;
import org.apache.commons.httpclient.methods.multipart.ByteArrayPartSource;
import org.apache.commons.httpclient.methods.multipart.FilePart;
import org.apache.commons.httpclient.methods.multipart.MultipartRequestEntity;
import org.apache.commons.httpclient.methods.multipart.Part;
import org.json.JSONObject;
import org.systemsbiology.addama.commons.httpclient.support.ApiKeyHttpClientTemplate;
import org.systemsbiology.addama.commons.httpclient.support.HttpClientTemplate;
import org.systemsbiology.addama.commons.httpclient.support.OkJsonResponseCallback;

import java.io.*;
import java.util.ArrayList;

/**
 * @author hrovira
 */
public class PrepChromIndexes {
    private static HttpClientTemplate httpClientTemplate;

    public static void main(String[] args) throws Exception {
        ApiKeyHttpClientTemplate template = new ApiKeyHttpClientTemplate();
        template.setApikey("60667408-363a-45a5-b771-42a8e4ecc0a7");
        template.afterPropertiesSet();
        httpClientTemplate = template;

        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(new File("/local/refgenomes/ucsc-hg18.txt"))));
        BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(baos));

        StringBuilder builder = new StringBuilder();
        builder.append("name");
        builder.append("\t");
        builder.append("chrom");
        builder.append("\t");
        builder.append("strand");
        builder.append("\t");
        builder.append("start");
        builder.append("\t");
        builder.append("end");
        builder.append("\t");
        builder.append("chromUri");
        builder.append("\t");
        builder.append("geneUri");
        writer.write(builder.toString());
        writer.newLine();

        String line = reader.readLine();
        while (line != null) {
            line = reader.readLine();
            if (line != null) {
                String[] splits = line.split("\t");
                String name = splits[1];
                String chrom = splits[2];
                String strand = splits[3];
                Integer txStart = Integer.parseInt(splits[4]);
                Integer txEnd = Integer.parseInt(splits[5]);
                String geneSymbol = splits[12];

                String chromUri = "/addama/refgenome/hg18/" + chrom + "/" + txStart + "/" + txEnd + "/" + strand;
                String geneUri = "/addama/refgenome/hg18/genes/" + geneSymbol;

                builder = new StringBuilder();
                builder.append(name);
                builder.append("\t");
                builder.append(chrom);
                builder.append("\t");
                builder.append(strand);
                builder.append("\t");
                builder.append(txStart);
                builder.append("\t");
                builder.append(txEnd);
                builder.append("\t");
                builder.append(chromUri);
                builder.append("\t");
                builder.append(geneUri);
                writer.write(builder.toString());
                writer.newLine();
            }
        }

        reader.close();
        writer.close();

        String directLink = getDirectLink("https://addama-systemsbiology-public.appspot.com/addama/datasources/write/transplantdb/chromosome-indexes");
        PostMethod post = new PostMethod(directLink);

        JSONObject config = new JSONObject();
        config.put("name", "text");
        config.put("chrom", "text");
        config.put("strand", "text");
        config.put("start", "int");
        config.put("end", "int");
        config.put("chromUri", "text");
        config.put("geneUri", "text");

        ArrayList<NameValuePair> nvps = new ArrayList<NameValuePair>();
        nvps.add(new NameValuePair("transform", "typeMap"));
        nvps.add(new NameValuePair("typeMap", config.toString()));
        post.setQueryString(nvps.toArray(new NameValuePair[nvps.size()]));

        Part bytePart = new FilePart("hg18-gene-chromosome-index", new ByteArrayPartSource("hg18-gene-chromosome-index", baos.toByteArray()));
        post.setRequestEntity(new MultipartRequestEntity(new Part[]{bytePart}, post.getParams()));

        System.out.println("json=" + httpClientTemplate.executeMethod(post, new OkJsonResponseCallback()));
    }

    private static String getDirectLink(String url) throws Exception {
        GetMethod get = new GetMethod(url + "/directlink");
        return (String) httpClientTemplate.executeMethod(get, new OkJsonResponseCallback() {
            public Object onResponse(int statusCode, HttpMethod method, JSONObject json) throws Exception {
                return json.getString("location");
            }
        });
    }


}
