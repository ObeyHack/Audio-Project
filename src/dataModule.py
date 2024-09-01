import lightning as pl
from litdata import StreamingDataLoader, StreamingDataset
from prep.processor import get_feature_extractor, get_tokenizer, FEATURES
import os
import torch


CLASSES = get_tokenizer().vocab_size + 1 # 1 for epsilon
BATCH_SIZE = 32

class SpeechStreamingDataset(StreamingDataset):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __getitem__(self, index):
            result = super().__getitem__(index)
            return result["mfcc"], result["mfcc_length"].squeeze(0), result["text_encoded"], result["text_length"].squeeze(0)


class AudioDataModule(pl.LightningDataModule):
    def __init__(self, data_dir: str = "/teamspace/s3_connections/audio-speech-hebrew",
                    train_dir: str = "ivrit-ai", 
                     batch_size: int = BATCH_SIZE):
        super().__init__()
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.train_dir = train_dir
        self._already_called = {}
        for stage in ("fit", "validate", "test", "predict"):
            self._already_called[stage] = False

    def setup(self, stage: str) -> None:
        if self._already_called[stage]:
            return

        if stage == "fit":
            # self.train_loader = StreamingDataLoader(SpeechStreamingDataset(input_dir=f"{self.data_dir}/train/{self.train_dir}"),
            #                                         batch_size=self.batch_size, shuffle=True, num_workers=os.cpu_count(),
            #                                          persistent_workers=True, pin_memory=True, subsample=0.1)

            self.train_loader = StreamingDataLoader(SpeechStreamingDataset(input_dir=f"/teamspace/studios/this_studio/preprocess/train/YV", ),
                                                    batch_size=self.batch_size,
                                                    shuffle=True, 
                                                    num_workers=os.cpu_count(),
                                                    persistent_workers=True, 
                                                    pin_memory=True)
            self._already_called["fit"] = True
            self.val_loader = StreamingDataLoader(SpeechStreamingDataset(input_dir=f"/teamspace/studios/this_studio/preprocess/train/YV", ),
                                                    batch_size=self.batch_size, 
                                                    shuffle=False, 
                                                    num_workers=os.cpu_count(),
                                                    persistent_workers=True, 
                                                    pin_memory=True,)

            # self.val_loader = StreamingDataLoader(SpeechStreamingDataset(input_dir=f"{self.data_dir}/val"),
            #                                         batch_size=self.batch_size, shuffle=False, num_workers=os.cpu_count(),
            #                                             persistent_workers=True, pin_memory=True)

            self._already_called["validate"] = True
            

        if stage == "validate" and not self._already_called["validate"]:
            self.val_loader = StreamingDataLoader(SpeechStreamingDataset(input_dir=f"{self.data_dir}/val"),
                                                    batch_size=self.batch_size, shuffle=False, num_workers=os.cpu_count(),
                                                        persistent_workers=True, pin_memory=True)
            self._already_called["validate"] = True

        if stage == "test":
            self.test_loader = StreamingDataLoader(SpeechStreamingDataset(input_dir=f"{self.data_dir}/test"),
                                                    batch_size=self.batch_size, shuffle=False, num_workers=os.cpu_count(),
                                                    persistent_workers=True, pin_memory=True)
            self._already_called["test"] = True

    def train_dataloader(self):
        return self.train_loader

    def val_dataloader(self):
        return self.val_loader

    def test_dataloader(self):
        return self.test_loader


def main():
    dm = AudioDataModule()
    dm.setup("fit")
    for batch in dm.train_dataloader():
        x, x_len, y, y_len = batch
        pass



if __name__ == "__main__":
    main()