from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-small-en")

def split_body(text):
    s=[]
    t=""
    for i in range(len(text)):
        t+=text[i]
        if i%300==0:
            s.append(t)
            t=""
    return s

def count_tokens(text):
    tokens = tokenizer.encode(
        text,
        add_special_tokens=True
    )
    return len(tokens)

def chunk_text(content):
    lines=content.split("\n")

    heads=[]
    i=0
    for line in lines:
        if '[head]' in line:
            heads.append(i)
        i+=1

    subs=[]
    temp=[]
    for i in range(len(heads)-1):
        if heads[i]-heads[i+1]==-1:
            temp.append(heads[i])
        
        else:
            temp.append(heads[i])
            subs.append(temp)
            temp=[]
    
    # print(subs)
    #if len > 1 in subs then its a hierarchy cluseter
    clusters=[x for x in subs if len(x)>=2]

    # print(clusters,'\n')

    chunks=[]

    heading_map=[]

    for i in range(len(clusters)-1):
        
        current_head=clusters[i][-1]

        next_head=clusters[i+1][0]

        for j in range(current_head,next_head):
            
            line=lines[j]

            if '[head]' in line:
                temp_map=[]

                for c in clusters[i][:-1]:
                    temp_map.append(c)

                temp_map.append(j)

                heading_map.append(temp_map)
    try:
        current_head=clusters[-1][-1]

        next_head=len(lines)

        for j in range(current_head,next_head):
            
            line=lines[j]
            # print(line)
            if '[head]' in line:

                temp_map=[]

                for c in clusters[-1][:-1]:
                    temp_map.append(c)

                temp_map.append(j)

                heading_map.append(temp_map)

    except Exception as e:print(e,"error handling last case")
    

    # print(heading_map)

    heading_tags=[]

    for i in heading_map:
        heading=""
        for j in i:
            txt=lines[j].replace(":","").replace('[head]',"").strip(" ")
            heading+=txt+" | "
        
        heading_tags.append(heading[:-3])

    body=[]

    for i in range(len(heading_map)-1):
        content=""

        for j in lines[heading_map[i][-1]+1:heading_map[i+1][-1]]:
            if '[Page]' not in j and '[head]' not in j:
                content+=j.replace("[body]","").strip(" ")+" "

        body.append(content)

    try:
        content=""

        for j in lines[heading_map[-1][-1]+1:len(lines)]:
            if '[Page]' not in j and '[head]' not in j:
                content+=j.replace("[body]","").strip(" ")+" "

        body.append(content)
    except:pass

    print(len(heading_tags))
    id=0
    for i in range(len(heading_map)):
        temp=dict()
        if len(body[i])>300:
            t=split_body(body[i])
            for j in t:
                temp['id']=id
                temp['title']=heading_tags[i]
                temp['content']=j
                temp['token']= count_tokens(body[i])
        else:
            temp['id']=id
            temp['title']=heading_tags[i]
            temp['content']=body[i]
            temp['token']= count_tokens(body[i])
        chunks.append(temp)
        id+=1
    # for i in chunks:print(f'{i['title']}: {i['content']} \n')
    return chunks

if __name__=='__main__':
    import pdf2txt as pdf
    print(chunk_text(pdf.get_content_from_pdf("../samples/bn1.pdf")))


        


        


    




























if __name__=='__main__':
    context="""[Page]

[head]EXTREME PDF STRUCTURE: 
[head]HEADING : SUBHEADING : 
[head]PARAGRAPH VALIDATION 
[head]Purpose: Testing Multi-Pattern Structural Recognition
[body]This document contains mixed formatting cases including inline bold text,
[body]colon-based titles, same-size bold subtitles, irregular spacing, embedded lists
[body]inside paragraphs, and structural interruptions.

[Page]

[head]1. PRIMARY ANALYTICAL SECTION :
[head]1.1 Structural Category Definition :
[head]Type 1.1A :
[body]Hierarchical parsing requires the identification of typographic markers. When a
[body]system encounters bold inline segments within standard text, it must determine
[body]whether the segment represents emphasis or structural hierarchy. Additionally,
[body]colon-terminated lines may indicate definitional headings.
[head]Interruption Case :
[body]This paragraph follows a bold line that has the same font size as the body text.
[body]Extraction algorithms must evaluate spacing, font weight, and contextual patterns.
[body]Incorrect classification may merge subtitles with surrounding paragraphs.
[body](cid:127) Font-size comparison logic.
[body](cid:127) Bold detection within identical font-size.
[body](cid:127) Colon-based heading termination rule.
[body]Following the bullet list, structural continuity resumes. A robust parser must
[body]reconnect semantic blocks while maintaining hierarchical awareness. Edge cases
[body]often occur when lists are nested between definitional subtitles.
[body]Element Type : Font Size Bold Colon Used
[body]Primary Section 20+ Yes Yes
[body]Subsection 16+ Yes Yes
[body]Inline Type 12 Yes Yes
[body]Paragraph 12 No No
[head]1.2 Structural Category Definition :
[head]Type 1.2A :
[body]Hierarchical parsing requires the identification of typographic markers. When a
[body]system encounters bold inline segments within standard text, it must determine
[body]whether the segment represents emphasis or structural hierarchy. Additionally,
[body]colon-terminated lines may indicate definitional headings.

[Page]

[head]Interruption Case :
[body]This paragraph follows a bold line that has the same font size as the body text.
[body]Extraction algorithms must evaluate spacing, font weight, and contextual patterns.
[body]Incorrect classification may merge subtitles with surrounding paragraphs.
[body](cid:127) Font-size comparison logic.
[body](cid:127) Bold detection within identical font-size.
[body](cid:127) Colon-based heading termination rule.
[body]Following the bullet list, structural continuity resumes. A robust parser must
[body]reconnect semantic blocks while maintaining hierarchical awareness. Edge cases
[body]often occur when lists are nested between definitional subtitles.
[body]Element Type : Font Size Bold Colon Used
[body]Primary Section 20+ Yes Yes
[body]Subsection 16+ Yes Yes
[body]Inline Type 12 Yes Yes
[body]Paragraph 12 No No
[head]1.3 Structural Category Definition :
[head]Type 1.3A :
[body]Hierarchical parsing requires the identification of typographic markers. When a
[body]system encounters bold inline segments within standard text, it must determine
[body]whether the segment represents emphasis or structural hierarchy. Additionally,
[body]colon-terminated lines may indicate definitional headings.
[head]Interruption Case :
[body]This paragraph follows a bold line that has the same font size as the body text.
[body]Extraction algorithms must evaluate spacing, font weight, and contextual patterns.
[body]Incorrect classification may merge subtitles with surrounding paragraphs.
[body](cid:127) Font-size comparison logic.
[body](cid:127) Bold detection within identical font-size.
[body](cid:127) Colon-based heading termination rule.
[body]Following the bullet list, structural continuity resumes. A robust parser must
[body]reconnect semantic blocks while maintaining hierarchical awareness. Edge cases
[body]often occur when lists are nested between definitional subtitles.

[Page]

[body]Element Type : Font Size Bold Colon Used
[body]Primary Section 20+ Yes Yes
[body]Subsection 16+ Yes Yes
[body]Inline Type 12 Yes Yes
[body]Paragraph 12 No No

[Page]

[head]2. PRIMARY ANALYTICAL SECTION :
[head]2.1 Structural Category Definition :
[head]Type 2.1A :
[body]Hierarchical parsing requires the identification of typographic markers. When a
[body]system encounters bold inline segments within standard text, it must determine
[body]whether the segment represents emphasis or structural hierarchy. Additionally,
[body]colon-terminated lines may indicate definitional headings.
[head]Interruption Case :
[body]This paragraph follows a bold line that has the same font size as the body text.
[body]Extraction algorithms must evaluate spacing, font weight, and contextual patterns.
[body]Incorrect classification may merge subtitles with surrounding paragraphs.
[body](cid:127) Font-size comparison logic.
[body](cid:127) Bold detection within identical font-size.
[body](cid:127) Colon-based heading termination rule.
[body]Following the bullet list, structural continuity resumes. A robust parser must
[body]reconnect semantic blocks while maintaining hierarchical awareness. Edge cases
[body]often occur when lists are nested between definitional subtitles.
[body]Element Type : Font Size Bold Colon Used
[body]Primary Section 20+ Yes Yes
[body]Subsection 16+ Yes Yes
[body]Inline Type 12 Yes Yes
[body]Paragraph 12 No No
[head]2.2 Structural Category Definition :
[head]Type 2.2A :
[body]Hierarchical parsing requires the identification of typographic markers. When a
[body]system encounters bold inline segments within standard text, it must determine
[body]whether the segment represents emphasis or structural hierarchy. Additionally,
[body]colon-terminated lines may indicate definitional headings.

[Page]

[head]Interruption Case :
[body]This paragraph follows a bold line that has the same font size as the body text.
[body]Extraction algorithms must evaluate spacing, font weight, and contextual patterns.
[body]Incorrect classification may merge subtitles with surrounding paragraphs.
[body](cid:127) Font-size comparison logic.
[body](cid:127) Bold detection within identical font-size.
[body](cid:127) Colon-based heading termination rule.
[body]Following the bullet list, structural continuity resumes. A robust parser must
[body]reconnect semantic blocks while maintaining hierarchical awareness. Edge cases
[body]often occur when lists are nested between definitional subtitles.
[body]Element Type : Font Size Bold Colon Used
[body]Primary Section 20+ Yes Yes
[body]Subsection 16+ Yes Yes
[body]Inline Type 12 Yes Yes
[body]Paragraph 12 No No
[head]2.3 Structural Category Definition :
[head]Type 2.3A :
[body]Hierarchical parsing requires the identification of typographic markers. When a
[body]system encounters bold inline segments within standard text, it must determine
[body]whether the segment represents emphasis or structural hierarchy. Additionally,
[body]colon-terminated lines may indicate definitional headings.
[head]Interruption Case :
[body]This paragraph follows a bold line that has the same font size as the body text.
[body]Extraction algorithms must evaluate spacing, font weight, and contextual patterns.
[body]Incorrect classification may merge subtitles with surrounding paragraphs.
[body](cid:127) Font-size comparison logic.
[body](cid:127) Bold detection within identical font-size.
[body](cid:127) Colon-based heading termination rule.
[body]Following the bullet list, structural continuity resumes. A robust parser must
[body]reconnect semantic blocks while maintaining hierarchical awareness. Edge cases
[body]often occur when lists are nested between definitional subtitles.

[Page]

[body]Element Type : Font Size Bold Colon Used
[body]Primary Section 20+ Yes Yes
[body]Subsection 16+ Yes Yes
[body]Inline Type 12 Yes Yes
[body]Paragraph 12 No No

[Page]

[head]3. PRIMARY ANALYTICAL SECTION :
[head]3.1 Structural Category Definition :
[head]Type 3.1A :
[body]Hierarchical parsing requires the identification of typographic markers. When a
[body]system encounters bold inline segments within standard text, it must determine
[body]whether the segment represents emphasis or structural hierarchy. Additionally,
[body]colon-terminated lines may indicate definitional headings.
[head]Interruption Case :
[body]This paragraph follows a bold line that has the same font size as the body text.
[body]Extraction algorithms must evaluate spacing, font weight, and contextual patterns.
[body]Incorrect classification may merge subtitles with surrounding paragraphs.
[body](cid:127) Font-size comparison logic.
[body](cid:127) Bold detection within identical font-size.
[body](cid:127) Colon-based heading termination rule.
[body]Following the bullet list, structural continuity resumes. A robust parser must
[body]reconnect semantic blocks while maintaining hierarchical awareness. Edge cases
[body]often occur when lists are nested between definitional subtitles.
[body]Element Type : Font Size Bold Colon Used
[body]Primary Section 20+ Yes Yes
[body]Subsection 16+ Yes Yes
[body]Inline Type 12 Yes Yes
[body]Paragraph 12 No No
[head]3.2 Structural Category Definition :
[head]Type 3.2A :
[body]Hierarchical parsing requires the identification of typographic markers. When a
[body]system encounters bold inline segments within standard text, it must determine
[body]whether the segment represents emphasis or structural hierarchy. Additionally,
[body]colon-terminated lines may indicate definitional headings.

[Page]

[head]Interruption Case : 
[body]This paragraph follows a bold line that has the same font size as the body text.
[body]Extraction algorithms must evaluate spacing, font weight, and contextual patterns.
[body]Incorrect classification may merge subtitles with surrounding paragraphs.
[body](cid:127) Font-size comparison logic.
[body](cid:127) Bold detection within identical font-size.
[body](cid:127) Colon-based heading termination rule.
[body]Following the bullet list, structural continuity resumes. A robust parser must
[body]reconnect semantic blocks while maintaining hierarchical awareness. Edge cases
[body]often occur when lists are nested between definitional subtitles.
[body]Element Type : Font Size Bold Colon Used
[body]Primary Section 20+ Yes Yes
[body]Subsection 16+ Yes Yes
[body]Inline Type 12 Yes Yes
[body]Paragraph 12 No No
[head]3.3 Structural Category Definition :
[head]Type 3.3A :
[body]Hierarchical parsing requires the identification of typographic markers. When a
[body]system encounters bold inline segments within standard text, it must determine
[body]whether the segment represents emphasis or structural hierarchy. Additionally,
[body]colon-terminated lines may indicate definitional headings.
[head]Interruption Case :
[body]This paragraph follows a bold line that has the same font size as the body text.
[body]Extraction algorithms must evaluate spacing, font weight, and contextual patterns.
[body]Incorrect classification may merge subtitles with surrounding paragraphs.
[body](cid:127) Font-size comparison logic.
[body](cid:127) Bold detection within identical font-size.
[body](cid:127) Colon-based heading termination rule.
[body]Following the bullet list, structural continuity resumes. A robust parser must
[body]reconnect semantic blocks while maintaining hierarchical awareness. Edge cases
[body]often occur when lists are nested between definitional subtitles.

[Page]

[body]Element Type : Font Size Bold Colon Used
[body]Primary Section 20+ Yes Yes
[body]Subsection 16+ Yes Yes
[body]Inline Type 12 Yes Yes
[body]Paragraph 12 No No

[Page]

[head]4. PRIMARY ANALYTICAL SECTION :
[head]4.1 Structural Category Definition :
[head]Type 4.1A :
[body]Hierarchical parsing requires the identification of typographic markers. When a
[body]system encounters bold inline segments within standard text, it must determine
[body]whether the segment represents emphasis or structural hierarchy. Additionally,
[body]colon-terminated lines may indicate definitional headings.
[head]Interruption Case :
[body]This paragraph follows a bold line that has the same font size as the body text.
[body]Extraction algorithms must evaluate spacing, font weight, and contextual patterns.
[body]Incorrect classification may merge subtitles with surrounding paragraphs.
[body](cid:127) Font-size comparison logic.
[body](cid:127) Bold detection within identical font-size.
[body](cid:127) Colon-based heading termination rule.
[body]Following the bullet list, structural continuity resumes. A robust parser must
[body]reconnect semantic blocks while maintaining hierarchical awareness. Edge cases
[body]often occur when lists are nested between definitional subtitles.
[body]Element Type : Font Size Bold Colon Used
[body]Primary Section 20+ Yes Yes
[body]Subsection 16+ Yes Yes
[body]Inline Type 12 Yes Yes
[body]Paragraph 12 No No
[head]4.2 Structural Category Definition :
[head]Type 4.2A :
[body]Hierarchical parsing requires the identification of typographic markers. When a
[body]system encounters bold inline segments within standard text, it must determine
[body]whether the segment represents emphasis or structural hierarchy. Additionally,
[body]colon-terminated lines may indicate definitional headings.

[Page]

[head]Interruption Case :
[body]This paragraph follows a bold line that has the same font size as the body text.
[body]Extraction algorithms must evaluate spacing, font weight, and contextual patterns.
[body]Incorrect classification may merge subtitles with surrounding paragraphs.
[body](cid:127) Font-size comparison logic.
[body](cid:127) Bold detection within identical font-size.
[body](cid:127) Colon-based heading termination rule.
[body]Following the bullet list, structural continuity resumes. A robust parser must
[body]reconnect semantic blocks while maintaining hierarchical awareness. Edge cases
[body]often occur when lists are nested between definitional subtitles.
[body]Element Type : Font Size Bold Colon Used
[body]Primary Section 20+ Yes Yes
[body]Subsection 16+ Yes Yes
[body]Inline Type 12 Yes Yes
[body]Paragraph 12 No No
[head]4.3 Structural Category Definition :
[head]Type 4.3A :
[body]Hierarchical parsing requires the identification of typographic markers. When a
[body]system encounters bold inline segments within standard text, it must determine
[body]whether the segment represents emphasis or structural hierarchy. Additionally,
[body]colon-terminated lines may indicate definitional headings.
[head]Interruption Case :
[body]This paragraph follows a bold line that has the same font size as the body text.
[body]Extraction algorithms must evaluate spacing, font weight, and contextual patterns.
[body]Incorrect classification may merge subtitles with surrounding paragraphs.
[body](cid:127) Font-size comparison logic.
[body](cid:127) Bold detection within identical font-size.
[body](cid:127) Colon-based heading termination rule.
[body]Following the bullet list, structural continuity resumes. A robust parser must
[body]reconnect semantic blocks while maintaining hierarchical awareness. Edge cases
[body]often occur when lists are nested between definitional subtitles.

[Page]

[body]Element Type : Font Size Bold Colon Used
[body]Primary Section 20+ Yes Yes
[body]Subsection 16+ Yes Yes
[body]Inline Type 12 Yes Yes
[body]Paragraph 12 No No

[Page]

[head]5. PRIMARY ANALYTICAL SECTION :
[head]5.1 Structural Category Definition :
[head]Type 5.1A :
[body]Hierarchical parsing requires the identification of typographic markers. When a
[body]system encounters bold inline segments within standard text, it must determine
[body]whether the segment represents emphasis or structural hierarchy. Additionally,
[body]colon-terminated lines may indicate definitional headings.
[head]Interruption Case :
[body]This paragraph follows a bold line that has the same font size as the body text.
[body]Extraction algorithms must evaluate spacing, font weight, and contextual patterns.
[body]Incorrect classification may merge subtitles with surrounding paragraphs.
[body](cid:127) Font-size comparison logic.
[body](cid:127) Bold detection within identical font-size.
[body](cid:127) Colon-based heading termination rule.
[body]Following the bullet list, structural continuity resumes. A robust parser must
[body]reconnect semantic blocks while maintaining hierarchical awareness. Edge cases
[body]often occur when lists are nested between definitional subtitles.
[body]Element Type : Font Size Bold Colon Used
[body]Primary Section 20+ Yes Yes
[body]Subsection 16+ Yes Yes
[body]Inline Type 12 Yes Yes
[body]Paragraph 12 No No
[head]5.2 Structural Category Definition :
[head]Type 5.2A :
[body]Hierarchical parsing requires the identification of typographic markers. When a
[body]system encounters bold inline segments within standard text, it must determine
[body]whether the segment represents emphasis or structural hierarchy. Additionally,
[body]colon-terminated lines may indicate definitional headings.

[Page]

[head]Interruption Case :
[body]This paragraph follows a bold line that has the same font size as the body text.
[body]Extraction algorithms must evaluate spacing, font weight, and contextual patterns.
[body]Incorrect classification may merge subtitles with surrounding paragraphs.
[body](cid:127) Font-size comparison logic.
[body](cid:127) Bold detection within identical font-size.
[body](cid:127) Colon-based heading termination rule.
[body]Following the bullet list, structural continuity resumes. A robust parser must
[body]reconnect semantic blocks while maintaining hierarchical awareness. Edge cases
[body]often occur when lists are nested between definitional subtitles.
[body]Element Type : Font Size Bold Colon Used
[body]Primary Section 20+ Yes Yes
[body]Subsection 16+ Yes Yes
[body]Inline Type 12 Yes Yes
[body]Paragraph 12 No No
[head]5.3 Structural Category Definition :
[head]Type 5.3A :
[body]Hierarchical parsing requires the identification of typographic markers. When a
[body]system encounters bold inline segments within standard text, it must determine
[body]whether the segment represents emphasis or structural hierarchy. Additionally,
[body]colon-terminated lines may indicate definitional headings.
[head]Interruption Case :
[body]This paragraph follows a bold line that has the same font size as the body text.
[body]Extraction algorithms must evaluate spacing, font weight, and contextual patterns.
[body]Incorrect classification may merge subtitles with surrounding paragraphs.
[body](cid:127) Font-size comparison logic.
[body](cid:127) Bold detection within identical font-size.
[body](cid:127) Colon-based heading termination rule.
[body]Following the bullet list, structural continuity resumes. A robust parser must
[body]reconnect semantic blocks while maintaining hierarchical awareness. Edge cases
[body]often occur when lists are nested between definitional subtitles.

[Page]

[body]Element Type : Font Size Bold Colon Used
[body]Primary Section 20+ Yes Yes
[body]Subsection 16+ Yes Yes
[body]Inline Type 12 Yes Yes
[body]Paragraph 12 No No"""

    chunk_text(context)