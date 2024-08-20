import * as React from 'react';
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import ButtonBase from '@mui/material/ButtonBase';
import Typography from '@mui/material/Typography';



const images = [
  {
    url: '/src/assets/Tram.png',
    title: 'Tram',
  },
  {
    url: '/src/assets/Bus.png',
    title: 'Bus',
  },

  {
    url: '/src/assets/Busstop.png',
    title: 'Stops',
  },


];

const ImageButton = styled(ButtonBase)(({ theme }) => ({
  position: 'relative',
  height: '100px',  
  width: '100px',   
  borderRadius: '50%',
  flexShrink: 0,     
  flexGrow: 0,
  overflow: 'hidden',
  margin: theme.spacing(1),    
  '&:hover, &.Mui-focusVisible': {
    zIndex: 1,
    '& .MuiImageBackdrop-root': {
      opacity: 0.15,
    },
    '& .MuiImageMarked-root': {
      opacity: 0,
    },
  },
}));

const ImageSrc = styled('span')({
  position: 'absolute',
  left: 0,
  right: 0,
  top: 0,
  bottom: 0,
  backgroundRepeat : 'no-repeat',
  backgroundSize: 'cover',
  borderRadius: '50%',
});

const Image = styled('span')(({ theme }) => ({
  position: 'absolute',
  left: 0,
  right: 0,
  top: 0,
  bottom: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: theme.palette.common.white,
  borderRadius: '50%',
  overflow: 'hidden'
}));

const ImageBackdrop = styled('span')(({ theme }) => ({
  position: 'absolute',
  left: 0,
  right: 0,
  top: 0,
  bottom: 0,
  backgroundColor: theme.palette.common.black,
  opacity: 0.4,
  transition: theme.transitions.create('opacity'),
}));

const ImageMarked = styled('span')(({ theme }) => ({
  height: 3,
  width: 18,
  backgroundColor: theme.palette.common.white,
  position: 'absolute',
  bottom: -2,
  left: 'calc(50% - 9px)',
  transition: theme.transitions.create('opacity'),
}));

export default function TramBusButton() {
  return (
    <Box sx={{ 
      display: 'flex', 
      flexWrap: 'wrap', 
      minWidth: 300, 
      width: '100%',
      justifyContent: 'center',
      alignItems: 'center',
      flexWrap: 'nowrap',
      overflow: 'hidden' }}>
      {images.map((image) => (
        <ImageButton
          focusRipple
          key={image.title}
          style={{
            width: '100 px',
            height: '100 px',
          }}
        >
          <ImageSrc style={{ backgroundImage: `url(${image.url})` }} />
          <ImageBackdrop className="MuiImageBackdrop-root" />
          <Image>
            <Typography
              component="span"
              variant="subtitle1"
              color="inherit"
              sx={{
                position: 'relative',
                p: 4,
                pt: 2,
                pb: (theme) => `calc(${theme.spacing(1)} + 6px)`,
              }}
            >
              {image.title}
              <ImageMarked className="MuiImageMarked-root" />
            </Typography>
          </Image>
        </ImageButton>
      ))}
    </Box>
  );
}
