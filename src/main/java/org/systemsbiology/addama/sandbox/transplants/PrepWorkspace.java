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
import org.apache.commons.httpclient.methods.multipart.FilePart;
import org.apache.commons.httpclient.methods.multipart.MultipartRequestEntity;
import org.apache.commons.httpclient.methods.multipart.Part;
import org.apache.commons.lang.StringUtils;
import org.json.JSONArray;
import org.json.JSONObject;
import org.springframework.context.ApplicationContext;
import org.springframework.context.support.ClassPathXmlApplicationContext;
import org.systemsbiology.addama.commons.httpclient.support.*;

import java.io.File;
import java.util.ArrayList;
import java.util.logging.Logger;

/**
 * @author hrovira
 */
public class PrepWorkspace {
    private static final Logger log = Logger.getLogger(PrepWorkspace.class.getName());

    private enum Phase {
        downloadSourceFile, uploadPatientModel, uploadPatientGeneScores, uploadTrack
    }

    private final HttpClientTemplate template;
    private final String workspaceUri;

    public PrepWorkspace(String apikey, String workspaceUri) {
        this.workspaceUri = workspaceUri;

        ApplicationContext appCtx = new ClassPathXmlApplicationContext("prepWorkspace.xml");
        ApiKeyHttpClientTemplate apikeyTemplate = (ApiKeyHttpClientTemplate) appCtx.getBean("httpClientTemplate");
        apikeyTemplate.setApikey(apikey);

        this.template = apikeyTemplate;
    }

    public static void main(String[] args) throws Exception {
        log.info("arguments:" + StringUtils.join(args, ","));
        if (args == null || args.length != 2) {
            throw new IllegalArgumentException("missing args: usage ( preprocessing | postprocessing ) queryString");
        }

        String queryString = StringUtils.replace(args[1], "\"", "");
        String apikey = getRequiredValue(queryString, "apikey");
        String wrkspc = getRequiredValue(queryString, "workspace");

        PrepWorkspace pw = new PrepWorkspace(apikey, wrkspc);
        switch (Phase.valueOf(args[0])) {
            case downloadSourceFile:
                pw.fetchSourceFile();
                break;
            case uploadPatientModel:
                pw.uploadModel();
                break;
            case uploadPatientGeneScores:
                pw.uploadPatientGeneScores();
                break;
            case uploadTrack:
                pw.uploadTrack();
                break;
        }
    }

    /*
     * Protected Methods
     */

    protected void fetchSourceFile() throws Exception {
        GetMethod get = new GetMethod(workspaceUri + "/sourceFile/dir");
        JSONObject json = (JSONObject) template.executeMethod(get, new OkJsonResponseCallback());
        if (!json.has("files")) {
            throw new IllegalArgumentException("no source file found in dataset");
        }

        JSONArray files = json.getJSONArray("files");
        if (files.length() < 0) {
            throw new IllegalArgumentException("no source file found in dataset");
        }

        JSONObject sourceFileJson = files.getJSONObject(0);
        if (!sourceFileJson.has("file")) {
            throw new IllegalArgumentException("no source file found in dataset");
        }

        String sourceFile = sourceFileJson.getString("file");
        File file = new File("sourceFile." + StringUtils.substringAfterLast(sourceFile, "."));
        GetMethod getFile = new GetMethod(sourceFile);
        getFile.setFollowRedirects(true);
        template.executeMethod(getFile, new PipeInputStreamContentResponseCallback(file));
    }

    protected void uploadModel() throws Exception {
        log.info("uploadModel");

        String uri = StringUtils.replace(workspaceUri, "/path/", "/file/") + "/models/create/directlink";
        String link = (String) template.executeMethod(new GetMethod(uri), new DirectLinkResponseCallback());

        PostMethod post = new PostMethod(link);
        FilePart filePart = new FilePart("patients", new File("patients.json"));
        post.setRequestEntity(new MultipartRequestEntity(new Part[]{filePart}, post.getParams()));

        template.executeMethod(post, new StatusCodeCaptureResponseCallback());
    }

    protected void uploadPatientGeneScores() throws Exception {
        log.info("uploadPatientGeneScores");

        JSONObject json = new JSONObject();
        json.put("patientgenescores", uploadDatasource(new File("patientgenescores.tsv"), "labeledDataMatrix", null));

        postDatasourceReference(workspaceUri + "/filedb", json);
    }

    protected void uploadTrack() throws Exception {
        log.info("uploadTrack");

        JSONObject trackConfig = new JSONObject();
        trackConfig.put("sample_id", "text");
        trackConfig.put("chr", "text");
        trackConfig.put("start", "double");
        trackConfig.put("span", "double");
        trackConfig.put("value", "double");

        JSONObject json = new JSONObject();
        json.put("track", uploadDatasource(new File("track.tsv"), "typeMap", trackConfig));

        postDatasourceReference(workspaceUri + "/filedb", json);
    }

    /*
     * Private Methods
     */

    private static String getRequiredValue(String queryString, String key) {
        String value = StringUtils.substringBetween(queryString, key + "=", "&");
        if (StringUtils.isEmpty(value)) {
            return StringUtils.substringAfterLast(queryString, key + "=");
        }
        if (StringUtils.isEmpty(value)) {
            throw new IllegalArgumentException(key + " is required in queryString");
        }
        return value;
    }

    private void postDatasourceReference(String uri, JSONObject json) throws Exception {
        PostMethod post = new PostMethod(uri + "/create");
        post.setQueryString(new NameValuePair[]{new NameValuePair("JSON", json.toString())});

        int statusCode = (Integer) template.executeMethod(post, new StatusCodeCaptureResponseCallback());
        if (statusCode == 409) {
            post = new PostMethod(uri);
            post.setQueryString(new NameValuePair[]{new NameValuePair("JSON", json.toString())});
            statusCode = (Integer) template.executeMethod(post, new StatusCodeCaptureResponseCallback());
        }
        log.info("postDatasourceReference(" + uri + "):" + statusCode);
    }

    private String uploadDatasource(File f, String transformUri, JSONObject config) throws Exception {
        log.info("uploadDatasource(" + f.getName() + "," + transformUri + ")");

        ArrayList<NameValuePair> nvps = new ArrayList<NameValuePair>();
        nvps.add(new NameValuePair("transform", transformUri));
        if (config != null) {
            nvps.add(new NameValuePair("typeMap", config.toString()));
        }

        String uri = "/addama/datasources/write/transplantdb" + workspaceUri + "/directlink";
        String link = (String) template.executeMethod(new GetMethod(uri), new DirectLinkResponseCallback());

        PostMethod post = new PostMethod(link);
        post.setQueryString(nvps.toArray(new NameValuePair[nvps.size()]));
        post.setRequestEntity(new MultipartRequestEntity(new FilePart[]{new FilePart(f.getName(), f)}, post.getParams()));

        JSONObject json = (JSONObject) template.executeMethod(post, new OkJsonResponseCallback());
        return json.getString("uri");
    }

    /*
     * Private Classes
     */

    private class DirectLinkResponseCallback extends OkJsonResponseCallback {
        public Object onResponse(int statusCode, HttpMethod method, JSONObject json) throws Exception {
            return json.getString("location");
        }
    }
}
