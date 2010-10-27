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

import org.apache.commons.lang.StringUtils;
import org.json.JSONObject;

import java.io.*;

/**
 * @author hrovira
 */
public class CreateGeneChromIndexFile {

    public static void main(String[] args) throws Exception {
        BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(new File("/local/refgenomes/gene_synonyms_index.idx"))));
        BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(new File("/local/temp/bulkload/gene_synonyms_index.csv"))));

        writer.write("\"uri\",\"json\"");
        writer.newLine();

        String line = reader.readLine();
        while (line != null) {
            line = reader.readLine();
            if (line != null) {
                String[] splits = line.split("\t");

                String geneUri = StringUtils.replace(splits[0], "/addama/indexes/synonyms/", "/addama/refgenome/hg18/genes/");

                JSONObject json = new JSONObject(splits[1]);
                if (json.has("Identifiers")) {
                    JSONObject identifiers = json.getJSONObject("Identifiers");
                    identifiers.remove("isLeaf");
                    identifiers.remove("isFile");
                }
                
                String jsonStr = StringUtils.replace(json.toString(), "\"", "\'");

                StringBuilder builder = new StringBuilder();
                builder.append("\"").append(geneUri).append("\"");
                builder.append(",");
                builder.append("\"").append(jsonStr).append("\"");
                writer.write(builder.toString());
                writer.newLine();
            }
        }

        reader.close();
        writer.close();
    }

}