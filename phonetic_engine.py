"""
Moteur de décomposition phonétique française
Trouve tous les mots possibles dans une séquence phonétique
"""

from phonemizer import phonemize
from collections import defaultdict
import re
import time

class PhoneticEngine:
    def __init__(self, dict_path='mots_francais.txt'):
        """Initialise le moteur avec le dictionnaire de mots"""
        self.word_to_phonetic = {}
        self.phonetic_to_words = defaultdict(list)
        self.word_frequencies = {}
        self._load_dictionary(dict_path)
        
    def _load_dictionary(self, path):
        """Charge le dictionnaire et convertit chaque mot en phonétique"""
        print(f"Chargement du dictionnaire depuis {path}...")
        start = time.time()
        
        with open(path, 'r', encoding='utf-8') as f:
            words = [line.strip().lower() for line in f if line.strip()]
        
        # Phonétisation par batch pour la performance
        batch_size = 1000
        for i in range(0, len(words), batch_size):
            batch = words[i:i+batch_size]
            try:
                phonetics = phonemize(
                    batch, 
                    language='fr-fr', 
                    backend='espeak',
                    strip=True,
                    preserve_punctuation=False,
                    with_stress=False
                )
                phonetics = phonetics.split('\n')
                
                for word, phon in zip(batch, phonetics):
                    if phon and len(word) > 1:  # Ignore mots trop courts
                        phon_clean = self._clean_phonetic(phon)
                        self.word_to_phonetic[word] = phon_clean
                        self.phonetic_to_words[phon_clean].append(word)
                        # Fréquence basée sur longueur (mots longs = plus rares)
                        self.word_frequencies[word] = 1.0 / (len(word) ** 0.5)
                        
            except Exception as e:
                print(f"Erreur batch {i}: {e}")
                continue
        
        elapsed = time.time() - start
        print(f"Dictionnaire chargé: {len(self.word_to_phonetic)} mots en {elapsed:.2f}s")
    
    def _clean_phonetic(self, phonetic):
        """Nettoie la représentation phonétique"""
        # Supprime les espaces et caractères spéciaux
        phonetic = phonetic.replace(' ', '').replace('ː', '')
        # Normalise certains caractères
        phonetic = phonetic.replace('ɛ̃', 'ɛ̃').replace('ɔ̃', 'ɔ̃').replace('œ̃', 'œ̃')
        return phonetic
    
    def text_to_phonetic(self, text):
        """Convertit un texte en phonétique"""
        try:
            phonetic = phonemize(
                text.lower(), 
                language='fr-fr', 
                backend='espeak',
                strip=True,
                preserve_punctuation=False,
                with_stress=False
            )
            return self._clean_phonetic(phonetic)
        except Exception as e:
            raise Exception(f"Erreur de phonétisation: {e}")
    
    def find_all_matches(self, phonetic_sequence, banned_words):
        """
        Trouve tous les mots qui matchent dans la séquence phonétique
        Retourne {position: [(mot, phonetic, end_position), ...]}
        """
        matches = defaultdict(list)
        seq_len = len(phonetic_sequence)
        
        for start in range(seq_len):
            for end in range(start + 1, seq_len + 1):
                substring = phonetic_sequence[start:end]
                
                if substring in self.phonetic_to_words:
                    for word in self.phonetic_to_words[substring]:
                        if word not in banned_words:
                            matches[start].append((word, substring, end))
        
        return matches
    
    def find_best_decompositions(self, text, top_n=3):
        """
        Trouve les meilleures décompositions du texte
        Retourne les top_n meilleures solutions
        """
        start_time = time.time()
        
        # Extraire les mots interdits
        banned_words = set(re.findall(r'\w+', text.lower()))
        
        # Convertir en phonétique
        phonetic = self.text_to_phonetic(text)
        print(f"Phonétique de '{text}': {phonetic}")
        
        # Trouver tous les matchs possibles
        matches = self.find_all_matches(phonetic, banned_words)
        
        # Recherche des meilleures décompositions avec programmation dynamique
        solutions = self._dp_solve(phonetic, matches)
        
        # Trier par score (moins de mots + exotisme)
        solutions.sort(key=lambda x: (len(x['words']), -x['exotic_score']))
        
        elapsed = time.time() - start_time
        
        return {
            'solutions': solutions[:top_n],
            'input_text': text,
            'phonetic': phonetic,
            'processing_time': elapsed,
            'total_solutions': len(solutions)
        }
    
    def _dp_solve(self, phonetic, matches):
        """
        Programmation dynamique pour trouver toutes les décompositions possibles
        Avec support des relations de challe (partage de phonèmes)
        """
        n = len(phonetic)
        # dp[i] = liste des solutions pour couvrir [0:i]
        dp = [[] for _ in range(n + 1)]
        dp[0] = [{'words': [], 'phonemes': [], 'positions': [], 'exotic_score': 0}]
        
        for i in range(n):
            if not dp[i]:
                continue
                
            for solution in dp[i]:
                # Option 1: Ajouter un mot qui commence à i
                if i in matches:
                    for word, phon, end in matches[i]:
                        new_solution = {
                            'words': solution['words'] + [word],
                            'phonemes': solution['phonemes'] + [phon],
                            'positions': solution['positions'] + [(i, end)],
                            'exotic_score': solution['exotic_score'] + self._calculate_exotic_score(word)
                        }
                        dp[end].append(new_solution)
                
                # Option 2: Relation de challe (partage d'un phonème)
                if i > 0 and i in matches:
                    for word, phon, end in matches[i]:
                        # Vérifier si le premier phonème de ce mot = dernier phonème du mot précédent
                        if solution['phonemes'] and len(phon) > 0:
                            last_phon = solution['phonemes'][-1]
                            if len(last_phon) > 0 and last_phon[-1] == phon[0]:
                                # Relation de challe possible
                                new_solution = {
                                    'words': solution['words'] + [f"[{word}]"],  # Marque la challe
                                    'phonemes': solution['phonemes'] + [phon],
                                    'positions': solution['positions'] + [(i, end)],
                                    'exotic_score': solution['exotic_score'] + self._calculate_exotic_score(word) * 1.2  # Bonus
                                }
                                dp[end].append(new_solution)
        
        # Convertir les solutions complètes
        complete_solutions = []
        for sol in dp[n]:
            complete_solutions.append({
                'words': sol['words'],
                'text': ' '.join([w.strip('[]') for w in sol['words']]),
                'exotic_score': sol['exotic_score']
            })
        
        return complete_solutions
    
    def _calculate_exotic_score(self, word):
        """
        Calcule le score d'exotisme d'un mot
        Plus le mot est long et rare, plus le score est élevé
        """
        length_score = len(word) ** 1.5
        rarity_score = 1.0 / (self.word_frequencies.get(word, 0.01))
        return length_score * rarity_score


# Test unitaire
if __name__ == "__main__":
    engine = PhoneticEngine()
    
    test_text = "je t'aime"
    results = engine.find_best_decompositions(test_text, top_n=3)
    
    print(f"\n=== Résultats pour '{test_text}' ===")
    print(f"Phonétique: {results['phonetic']}")
    print(f"Temps: {results['processing_time']:.2f}s")
    print(f"Solutions trouvées: {results['total_solutions']}")
    print("\nTop 3:")
    for i, sol in enumerate(results['solutions'], 1):
        print(f"{i}. {sol['text']} ({len(sol['words'])} mots, score: {sol['exotic_score']:.2f})")
