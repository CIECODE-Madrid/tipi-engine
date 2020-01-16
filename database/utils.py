def clean_content(initiative):

    def delete_commission_if_appears_on_pnl(text, initiative_type):
        if initiative_type != '161':
            return text
        try:
            phrases = text.split('.')
            if len(phrases) == 1:
                return text
            if phrases[len(phrases)-1].find('  Comisión') == -1:
                return text
            return ''.join(phrases[:len(phrases)-1])
        except:
            return text

    try:
        new_content = list()
        for paragraph in initiative['content']:
            if type(paragraph) is list and len(paragraph) == 1:
                new_paragraph = paragraph[0]
            else:
                new_paragraph = paragraph
            paragraph_mod = delete_commission_if_appears_on_pnl(
                    new_paragraph,
                    initiative['initiative_type']
                    )
            for phrase in paragraph_mod.split('.'):
                new_content.append(phrase)
    except:
        pass
    initiative['content'] = new_content
