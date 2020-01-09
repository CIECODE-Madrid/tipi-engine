from database.congreso import Congress


class CleanContents:

    def __init__(self):
        self.dbmanager = Congress()

    def clean(self):
        initiatives = self.dbmanager.searchByParams('initiatives')
        for initiative in initiatives:
            try:
                new_content = list()
                for paragraph in initiative['content']:
                    if type(paragraph) is list and len(paragraph) == 1:
                        new_paragraph = paragraph[0]
                    else:
                        new_paragraph = paragraph
                    new_content.append(
                            self.__delete_commission_if_appears_on_pnl(
                                new_paragraph,
                                initiative['initiative_type']
                                )
                            )
                self.dbmanager.updateInitiativeContent(
                        initiative['_id'],
                        new_content
                        )
            except:
                pass

    def __delete_commission_if_appears_on_pnl(self, text, initiative_type):
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
